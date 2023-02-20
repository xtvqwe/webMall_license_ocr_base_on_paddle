from datetime import datetime
import time
from paddleocr import PaddleOCR
import numpy as np
import cv2
import os
import re
import json

def get_names():
    fsp='./ocr/static/tmp_license/'
    files=os.listdir(fsp)
    names=[fsp+x for x in files]
    return names

def file_split(names):
    ids_s=[]
    reports=[]
    fnames=[]
    for nid in range(len(names)):
        name=names[nid]
        ids=name.replace('./ocr/static/tmp_license/prove_','').replace('.jpg','').split('_')
        if len(ids)==1:
            fnames.append(name)
        else:
            ids_s.append(ids)
    ids_sorted=sorted(ids_s,key=lambda x:x[1],reverse=False)
    for id_s in ids_sorted:
        id_include=[x for x in ids_sorted if x[0]==id_s[0]]
        if len(id_include)==1:
            fnames.append('./ocr/static/tmp_license/prove_'+'_'.join(id_s)+'.jpg')
        else:
            report_s=['./ocr/static/tmp_license/prove_'+'_'.join(x)+'.jpg' for x in id_include]
            if report_s not in reports:
                reports.append(report_s)
    return fnames,reports

def ocr_df(names):
    ocr=PaddleOCR(
            #rec_module_dir='C:/Users/admin/AppData/Local/Programs/Python/Python39/Lib/site-packages/paddleocr/2.0/ch_ppocr_server_v2.0_rec_infer',
            #cls_module_dir='C:/Users/admin/AppData/Local/Programs/Python/Python39/Lib/site-packages/paddleocr/2.0/ch_ppocr_server_v2.0_cls_infer',
            #det_module_dir='C:/Users/admin/AppData/Local/Programs/Python/Python39/Lib/site-packages/paddleocr/2.0/ch_ppocr_server_v2.0_det_infer'
        )
    ocr_df=[]
    shapes_df=[]
    for name in names:
        img=cv2.imread(name,0)
        shapes_df.append(np.shape(img))
        result=ocr.ocr(img)
        ocr_df.append(result)
        #testp_ocr([result])
        time.sleep(1)
    return ocr_df,shapes_df

def type_split(datas,shapes):
    types=[]
    for result_i in range(len(datas)):
        result=datas[result_i]
        #squares=[]
        sqr_results=[]
        img_shape=shapes[result_i]
        if len(result)>0:
            #取最上方的识别文字
            #testp_ocr([sorted(result,key=lambda x:x[0][0][1],reverse=False)])
            result_lt=sorted(result,key=lambda x:x[0][0][1],reverse=False)[0][1][0]
            text_list=[]
            for si in range(len(result)):
                text=result[si][1][0].replace(':','').replace('：','')
                text_list.append(text)
                s=[x for x in result[si][0] if x[1]<img_shape[1]//2]
                ssws=[x[0] for x in s]
                sshs=[x[1] for x in s]
                if len(sshs)>0:
                    ssw=max(ssws)-min(ssws)
                    ssh=max(sshs)-min(sshs)
                    sqr_pw=(ssw*ssh)//len(result[si][1][0])
                    sqr_results.append([sqr_pw,result[si]])
            squares=sorted(sqr_results,key=lambda x:x[0],reverse=True)
            #if squares[0][1][1][0]=='MA' or len(squares[0][1][1][0])>10 or '商标注册证' in squares[1][1][1][0] or '商标续展注册证明' in squares[1][1][1][0]:
            #    max_result=squares[1][1]
            #else:
            #    max_result=squares[0][1]
            if squares[0][1][1][0]=='MA' or '商标续展注册证明' in squares[1][1][1][0] or len(squares[0][1][1][0])<3:
                max_result=squares[1][1]
            else:
                max_result=squares[0][1]
            
            #print(squares)
            #testp_ocr(squares)
            title=max_result[1][0]
            #print(max_result)
        else:
            title=''
        if title=='营业执照':
            types.append('b_license')
        elif '经营许可证' in title:
            types.append('oper_permit')
        elif '食品生产许可证' in title:
            types.append('food_permit')
        elif '商标注册证' in title:
            types.append('label_regist')
        elif '检测报告' in title or '检验报告' in title or ('样品名称' in text_list and '委托单位' in text_list):
            types.append('reports')
        elif '商标转让证明' in title:
            types.append('label_transfer')
        elif '商标续展注册证明' in title:
            types.append('label_continue')
        elif '注册商标变更证明' in title:
            types.append('label_change')

        else:
            if result_lt=='承诺函':
                types.append('commit_letter')
            elif result_lt=='更名通知':
                types.append('change_name_memo')
            elif result_lt=='授权书':
                types.append('label_permission')
            elif '商标' in result_lt and '使用' in result_lt and '许可' in result_lt:
                types.append('label_permission')
            elif '品牌授权' in result_lt:
                types.append('label_permission')
            elif result_lt=='旗舰店授权':
                types.append('store_permission')
            elif result_lt=='产品委托加工协议':
                types.append('product_proxies')
            else:
                types.append('')
    return types

def get_messges(data,keys):
    match_data=[]
    for objk in keys:
        obj=[]
        value=''
        for result in data:
            if objk in result[1][0].replace(' ',''):
                obj=result
                if objk in obj[1][0].replace(' ','')[-(len(objk)+1):]:
                    k_hs=[x[1] for x in obj[0]]
                    k_ws=[x[0] for x in obj[0]]
                    max_kh=max(k_hs)
                    min_kh=min(k_hs)
                    kw_r=(max(k_ws)-min(k_ws))//2+min(k_ws)
                    kheight=max_kh-min_kh
                    minkh=min_kh-kheight
                    maxkh=max_kh+kheight
                    break
                else:
                    value=obj[1][0].replace(' ','').split(objk)[1].replace('：','').replace(':','')
        if value=='' and obj!=[]:
            raw_matches=[]
            for r1 in data:
                r1p=r1[0]
                r1hs=[x[1] for x in r1p]
                r1ws=[x[0] for x in r1p]
                #在上下各一行高度区间内,且在标识内容右侧
                if min(r1hs)>minkh and max(r1hs)<maxkh and min(r1ws)>=kw_r:
                    raw_matches.append(r1)
            matches=sorted(raw_matches,key=lambda x:x[0][0][0],reverse=False)
            if len(matches)>0:
                match_obj=matches[0]
                obj_ws=[match_obj[0][x][0] for x in range(4)]
                #最右点位
                mobj_r=max(obj_ws)
                #偏移量计算
                objw_sort=sorted(obj_ws,reverse=True)
                obj_shift=objw_sort[0]-objw_sort[1]
                #包含内容最右侧点位在最接近标识内容范围内(符合换行上长下短格式)
                match_vs=[x[1][0] for x in matches if max([y[0] for y in x[0]])<mobj_r+obj_shift]
                value=match_obj[1][0]+''.join(match_vs)
        match_data.append(value)
    return match_data

#承诺函信息提取
def commit_data(results):
    cldatas=[]
    for i in range(len(results)):
        img_name=results[i][1]
        r=results[i][0]
        cname=''
        for data in r:
            if '以下简称' in data[1][0] and '我司' in data[1][0]:
                cname=data[1][0].split('公司')[0]+'公司'
                break
        cldatas.append([[cname],img_name])
    return cldatas

#商标授权
def label_permissions(lprs):
    lpr_s=[]
    for lpr_data in lprs:
        lpr=lpr_data[0]
        fname=lpr_data[1]
        guestwords=''
        hostwords=''
        number_strs=''
        datas=sorted(lpr,key=lambda x:x[0][1][1],reverse=False)
        for data_i in range(len(datas)):
            data=datas[data_i]
            if '被许可人' in data[1][0] or '被授权人' in data[1][0]:
                if ':' in data[1][0]:
                    guestwords=data[1][0].split(':')[1]
                elif '：' in data[1][0]:
                    guestwords=data[1][0].split('：')[1]
            elif '许可人' in data[1][0] or '授权人' in data[1][0]:
                if ':' in data[1][0]:
                    hostwords=data[1][0].split(':')[1]
                elif '：' in data[1][0]:
                    hostwords=data[1][0].split('：')[1]
            elif '注册号' or '商标号' in data[1][0]:
                for num_i in range(data_i,len(datas)):
                    number_strs+=datas[num_i][1][0]
        numbers=re.findall('\d+',number_strs)
        label_codes=[]
        for num in numbers:
            if num not in label_codes and len(num)>4:
                label_codes.append(num)
        lpr_s.append([[guestwords,hostwords,label_codes],fname])
    return lpr_s 

#商标注册
def label_registion(lrrs):
    lrr_s=[]
    lrns=[]
    lrfns=[]
    lrdatas=[]
    for lrri in range(len(lrrs)):
        lrr=lrrs[lrri][0]
        lrsr=lrrs[lrri][1]
        lrfn=lrrs[lrri][2]
        lrfns.append(lrfn)
        #注册号
        label_code=''
        lrr_sort=sorted(lrr,key=lambda x:x[0][0][1],reverse=False)
        lrr_cr=[x for x in lrr_sort if x[0][0][0]>lrsr[0]//2 and x[0][0][1]<lrsr[1]//2]
        lr_str=''
        for lrw in lrr_cr:
            lr_str+=lrw[1][0]
        label_code_s=re.findall('\d+',lr_str)
        if len(label_code_s)>0:
            label_code=label_code_s[0]
        lrr_s.append(label_code)
        lrn=''
        for lrdi in range(len(lrr_sort)):
            if lrr_sort[lrdi][1][0]=='注册人':
                row_data_raw=[]
                hs=[x[1] for x in lrr_sort[lrdi][0]]
                minh=min(hs)
                maxh=max(hs)
                hspace=maxh-minh
                for lrd in lrr_sort:
                    lrdhs=[x[1] for x in lrd[0]]
                    if min(lrdhs)>minh-hspace and max(lrdhs)<maxh+hspace and lrd[1][0]!=lrr_sort[lrdi][1][0]:
                        row_data_raw.append(lrd)
                        #print(lrd)
                row_data=sorted(row_data_raw,key=lambda x:x[0][0][1],reverse=False)
                lrn=''.join([x[1][0] for x in row_data])
                break
            elif lrr_sort[lrdi][1][0][:3]=='注册人' and lrr_sort[lrdi][1][0][3:5]!='地址':
                lrn=lrr_sort[lrdi][1][0][3:]
                break
        lrns.append(lrn)
        lrdatas.append([[label_code,lrn],lrfn])
    return lrr_s,lrns,lrfns,lrdatas

#商标转让
def label_transfer(lts):
    ltrs=[]
    for lt_r in lts:
        ltn=lt_r[1]
        lt=lt_r[0]
        ltnum=''
        transfer=''
        for ltr in lt:
            if '兹核准第' in ltr[1][0] and '号商标转让注册' in ltr[1][0]:
                ltnum=re.findall('\d+',ltr[1][0])[0]
            if ltr[1][0][:5]=='受让人名称':
                transfer=ltr[1][0][5:]
        ltrs.append([[ltnum,transfer],ltn])
    return ltrs

#商标变更
def label_change(lts):
    ltrs=[]
    for lt_r in lts:
        ltn=lt_r[1]
        lt=lt_r[0]
        ltnum=''
        transfer=''
        for ltri in range(len(lt)):
            ltr=lt[ltri]
            if '兹核准第' in ltr[1][0] and '号商标注册人名义变更' in ltr[1][0]:
                ltnum=re.findall('\d+',ltr[1][0])[0]
            if ltr[1][0][:8]=='变更后注册人名义':
                transfer=ltr[1][0][8:]
            elif ltr[1][0][-8:]=='变更后注册人名义':
                transfer=lt[ltri+1][1][0]
        ltrs.append([[ltnum,transfer],ltn])
    return ltrs

#商标续展
def label_continue(lcs):
    lcrs=[]
    for lc_r in lcs:
        lcn=lc_r[1]
        lc=lc_r[0]
        lc_code=''
        for lcr in lc:
            if '兹核准第' in lcr[1][0] and '续展注册' in lcr[1][0]:
                lc_code=re.findall('\d+',lcr[1][0])[0]
                break
        lcrs.append([[lc_code],lcn])
    return lcrs

def reports_d(report_s):
    rkeys=['样品名称','产品名称','委托单位']
    rdata=[]
    for rpt in report_s:
        rptd=rpt[0]
        rpt_r=get_messges(rptd,rkeys)
        if rpt_r[0]!='':
            rdata.append([[rpt_r[2],rpt_r[0]],rpt[1]])
        else:
            rdata.append([[rpt_r[2],rpt_r[1]],rpt[1]])
    return rdata


#匹配函数
def match_datas(datas):
    alldatas=[]
    for tdatas in datas:
        for tdata in tdatas:
            alldatas.append(tdata)

    mdatas=[]
    matched_pics=[]
    for bm in datas[0]:
        bop=''
        bopname=''
        bfname=''
        bopt=''
        b_f=''
        bft=''
        bc=''
        bls=[]
        bps=[]
        brpts=[]
        matched_pics.append(bm[2])
        for opm in datas[1]:
            if opm[1][0]==bm[1][0]:
                bop=opm[2]
                bopname=opm[1][0]
                bopt=opm[1][1]
                matched_pics.append(opm[2])
                break
        for fm in datas[2]:
            if fm[1][0]==bm[1][0]:
                b_f=fm[2]
                bft=fm[1][1]
                matched_pics.append(fm[2])
                break
        for cm in datas[3]:
            if cm[1][0]==bm[1][0]:
                bc=cm[2]
                matched_pics.append(cm[2])
                break
        #商标注册
        for lm in datas[4]:
            if lm[1][1]==bm[1][0]:
                bls.append(lm[2])
                lmlc=[x[2] for x in datas[8] if x[1][0]==lm[1][0]][0]
                bls.append(lmlc)
                matched_pics.append(lm[2])
                matched_pics.append(lmlc)
                break
        #商标授权
        if len(bls)==0:
            for lp in datas[5]:
                if lp[1][1]==bm[1][0]:
                    lplr=[x[2] for x in datas[4] if x[1][0]==lp[1][0]][0]
                    bls.append(lplr)
                    bls.append(lp[2])
                    lplc=[x[2] for x in datas[8] if x[1][0]==lp[1][0]][0]
                    bls.append(lplc)
                    matched_pics.append(lplr)
                    matched_pics.append(lp[2])
                    matched_pics.append(lplc)
                    break
        #商标转让
        if len(bls)==0:
            for lt in datas[6]:
                if lt[1][1]==bm[1][0]:
                    ltlr=[x[2] for x in datas[4] if x[1][0]==lt[1][0]][0]
                    bls.append(ltlr)
                    bls.append(lt[2])
                    ltlc=[x[2] for x in datas[8] if x[1][0]==lt[1][0]][0]
                    bls.append(ltlc)
                    matched_pics.append(ltlr)
                    matched_pics.append(lt[2])
                    matched_pics.append(ltlc)
                    break
        #商标变更
        if len(bls)==0:
            for lct in datas[7]:
                if lct[1][1]==bm[1][0]:
                    lctlr=[x[2] for x in datas[4] if x[1][0]==lct[1][0]][0]
                    bls.append(lctlr)
                    bls.append(lct[2])
                    lctlc=[x[2] for x in datas[8] if x[1][0]==lct[1][0]][0]
                    bls.append(lctlc)
                    matched_pics.append(lctlr)
                    matched_pics.append(lct[2])
                    matched_pics.append(lctlc)
                    break
        for rpt in datas[9]:
            if rpt[1][1]==bm[1][0]:
                brpts.append(rpt[2])
                matched_pics.append(rpt[2])
                bps.append(rpt[1][0])
        mdatas.append({
            'bname':'_'.join([bm[1][0],bm[1][1]]),
            'fname':'_'.join([bm[1][0],bft]),
            'bf':bm[2].split('/')[-1],
            'opn':'_'.join([bopname,bopt]),
            'opf':bop.split('/')[-1],
            'cf':bc.split('/')[-1],
            'pf':b_f.split('/')[-1],
            'brand_fs':[x.split('/')[-1] for x in bls],
            'pns':bps,
            'brpts_fs':[x.split('/')[-1] for x in brpts]
        }.copy())
    
    unmatch_fmessages=[x for x in datas[2] if x[2] not in matched_pics]

    for ufm in unmatch_fmessages:
        fop=''
        fopname=''
        fopt=''
        f_f=ufm[2]
        fft=ufm[1][1]
        fc=''
        fls=[]
        fps=[]
        frpts=[]
        matched_pics.append(ufm[2])
        for opm in datas[1]:
            if opm[1][0]==ufm[1][0]:
                fop=opm[2]
                fopname=opm[1][0]
                fopt=opm[1][1]
                matched_pics.append(opm[2])
                break
        for cm in datas[3]:
            if cm[1][0]==ufm[1][0]:
                fc=cm[2]
                matched_pics.append(cm[2])
                break
        for lm in datas[4]:
            if lm[1][1]==ufm[1][0]:
                fls.append(lm[2])
                lmlc=[x[2] for x in datas[8] if x[1][0]==lm[1][0]][0]
                fls.append(lmlc)
                matched_pics.append(lm[2])
                matched_pics.append(lmlc)
                break
        if len(fls)==0:
            for lp in datas[5]:
                if lp[1][1]==ufm[1][0]:
                    lplr=[x[2] for x in datas[4] if x[1][0]==lp[1][0]][0]
                    fls.append(lplr)
                    fls.append(lp[2])
                    lplc=[x[2] for x in datas[8] if x[1][0]==lp[1][0]][0]
                    fls.append(lplc)
                    matched_pics.append(lplr)
                    matched_pics.append(lp[2])
                    matched_pics.append(lplc)
                    break
        if len(fls)==0:
            for lt in datas[6]:
                if lt[1][1]==ufm[1][0]:
                    ltlr=[x[2] for x in datas[4] if x[1][0]==lt[1][0]][0]
                    fls.append(ltlr)
                    fls.append(lt[2])
                    ltlc=[x[2] for x in datas[8] if x[1][0]==lt[1][0]][0]
                    fls.append(ltlc)
                    matched_pics.append(ltlr)
                    matched_pics.append(lt[2])
                    matched_pics.append(ltlc)
                    break
        if len(fls)==0:
            for lct in datas[7]:
                if lct[1][1]==ufm[1][0]:
                    lctlr=[x[2] for x in datas[4] if x[1][0]==lct[1][0]][0]
                    fls.append(lctlr)
                    fls.append(lct[2])
                    lctlc=[x[2] for x in datas[8] if x[1][0]==lct[1][0]][0]
                    fls.append(lctlc)
                    matched_pics.append(lctlr)
                    matched_pics.append(lct[2])
                    matched_pics.append(lctlc)
                    break
        for rpt in datas[8]:
            if rpt[1][1]==ufm[1][0]:
                frpts.append(rpt[2])
                matched_pics.append(rpt[2])
                fps.append(rpt[1][0])
        mdatas.append({
            'bname':'',
            'fname':'_'.join([ufm[1][0],fft]),
            'bf':'',
            'opn':'_'.join([fopname,fopt]),
            'opf':fop.split('/')[-1],
            'cf':fc.split('/')[-1],
            'pf':f_f.split('/')[-1],
            'brand_fs':[x.split('/')[-1] for x in fls],
            'pns':fps,
            'brpts_fs':[x.split('/')[-1] for x in frpts]
        }.copy())
    
    unmatch_alldata=[x for x in alldatas if x[2] not in matched_pics]

    return alldatas,unmatch_alldata,mdatas

def multi_subject(datas):
    label_ids=[]
    obj_datas=[]
    relative_raw=[]
    for pdatas in datas:
        for pdata in pdatas:
            obj_datas.append(pdata)
            if pdata[0]=='商标授权':
                relative_sub=[x for x in pdata[1][:2] if x!='']
                if pdata[1][1]!='':
                    label_ids+=[[pdata[1][1],x] for x in pdata[1][2]]
                elif pdata[1][0]!='':
                    label_ids+=[[pdata[1][0],x] for x in pdata[1][2]]
            elif pdata[0] in ['营业执照','经营许可','生产许可','承诺函','检验报告']:
                if pdata[1][0]!='':
                    relative_sub=[pdata[1][0]]
                    #relative_names.append([pdata[1][0]])
            elif pdata[0] in ['商标注册证','商标转让','商标变更']:
                if pdata[1][1]!='':
                    relative_sub=[pdata[1][1]]
                    #relative_names.append([pdata[1][1]])
                l_array=pdata[1]
                if l_array not in label_ids and pdata[1][0]!='':
                    label_ids.append(l_array)    
            relative_raw.append(relative_sub)
    relative_names=[]
    for rawsub in relative_raw:
        for rawsub1 in relative_raw:
            for rawunit in rawsub1:
                if rawunit in rawsub:
                    rawsub2=rawsub+rawsub1
        sub_new=list(set(rawsub2))
        if sub_new not in relative_names:
            print(sub_new)
            relative_names.append(sub_new)
    label_cs=[]
    for label_c in label_ids:
        for lobj in obj_datas:
            if lobj[0]=='商标续展' and lobj[1][0]==label_c[0]:
                label_cs.append([label_c,lobj[2]])
                break
    types=['营业执照','经营许可','生产许可','承诺函','商标注册证','商标授权','商标转让','商标变更','商标续展','检验报告']
    result=[]
    mpics=[]
    for rnames in relative_names:
        subdata=[rnames]
        for otype in types:
            objdata=[]            
            for obj in obj_datas:
                if otype in ['营业执照','经营许可','生产许可','承诺函']:
                    if obj[0]==otype and obj[1][0] in rnames:
                        objdata=['_'.join(obj[1]),obj[2]]
                        mpics.append(obj[2])
                        break
                elif otype in ['商标注册证','商标转让','商标变更']:
                    if obj[0]==otype and obj[1][1] in rnames:
                        objdata=['_'.join(obj[1]),obj[2]]
                        mpics.append(obj[2])
                        break
                elif otype=='商标授权':
                    if obj[0]==otype and (obj[1][1] in rnames or obj[1][0] in rnames):
                        objdata=obj[1]+[obj[2]]
                        mpics.append(obj[2])
                        break
            if otype=='商标续展':
                for labelc_data in label_cs:
                    if labelc_data[0][1] in rnames:
                        objdata=['_'.join(labelc_data[0]),labelc_data[1]]
                        mpics.append(labelc_data[1])
                        break
            elif otype=='检验报告':
                pnames=[]
                for robj in obj_datas:
                    if robj[0]==otype and robj[1][0] in rnames:
                        pnames.append([robj[1][0],robj[1][1],robj[2]])
                        mpics.append(robj[2])
                objdata=pnames
            subdata.append(objdata)

        sub_keys=['subject','license','operation','product','commit','label_r','label_p','laber_t','label_change','label_continue','rpts']
        subdic=dict(zip(sub_keys,subdata))
        #print(subdic)
        result.append(subdic)
    print(result)
    return {'mdata':result}


def get_datas():
    names=get_names()
    fnames,reports=file_split(names)
    t_names=fnames+[x[0] for x in reports]
    ocr_datas,ocr_shapes=ocr_df(t_names)
    types=type_split(ocr_datas,ocr_shapes)
    bl_rs=[[ocr_datas[x],t_names[x]] for x in range(len(types)) if types[x]=='b_license']
    op_rs=[[ocr_datas[x],t_names[x]] for x in range(len(types)) if types[x]=='oper_permit']
    fp_rs=[[ocr_datas[x],t_names[x]] for x in range(len(types)) if types[x]=='food_permit']
    cl_rs=[[ocr_datas[x],t_names[x]] for x in range(len(types)) if types[x]=='commit_letter']
    report_s=[[ocr_datas[x],t_names[x]] for x in range(len(types)) if types[x]=='reports']
    pkeys=['称','效期至']
    lkeys=['称','期限']
    fkeys=['称','日期至']
    rkeys=['样品名称','委托单位']

    lr_rs=[[ocr_datas[x],ocr_shapes[x],t_names[x]] for x in range(len(types)) if types[x]=='label_regist']
    lp_rs=[[ocr_datas[x],t_names[x]] for x in range(len(types)) if types[x]=='label_permission']
    lt_s=[[ocr_datas[x],t_names[x]] for x in range(len(types)) if types[x]=='label_transfer']
    lchange_s=[[ocr_datas[x],t_names[x]] for x in range(len(types)) if types[x]=='label_change']
    lc_s=[[ocr_datas[x],t_names[x]] for x in range(len(types)) if types[x]=='label_continue']
    if bl_rs!=[]:
        bmessages=[['营业执照',get_messges(x[0],lkeys),x[1]] for x in bl_rs]
    else:
        bmessages=[]
    if op_rs!=[]:
        opmessages=[['经营许可',get_messges(x[0],pkeys),x[1]] for x in op_rs]
    else:
        opmessages=[]
    if fp_rs!=[]:
        fmessages=[['生产许可',get_messges(x[0],fkeys),x[1]] for x in fp_rs]
    else:
        fmessages=[]
    if cl_rs!=[]:
        cmessages=[['承诺函',x[0],x[1]] for x in commit_data(cl_rs)]
    else:
        cmessages=[]
    if lr_rs!=[]:
        lrmessages=[['商标注册证',x[0],x[1]] for x in label_registion(lr_rs)[3]]
    else:
        lrmessages=[]
    if lp_rs!=[]:
        lpmessages=[['商标授权',x[0],x[1]] for x in label_permissions(lp_rs)]
    else:
        lpmessages=[]
    if lt_s!=[]:
        ltmessages=[['商标转让',x[0],x[1]] for x in label_transfer(lt_s)]
    else:
        ltmessages=[]
    if lchange_s!=[]:
        lchangemessages=[['商标变更',x[0],x[1]] for x in label_change(lchange_s)]
    else:
        lchangemessages=[]
    if lc_s!=[]:
        lcmessages=[['商标续展',x[0],x[1]] for x in label_continue(lc_s)]
    else:
        lcmessages=[]
    if report_s!=[]:
        rptmessages=[['检验报告',x[0],x[1]] for x in reports_d(report_s)]
    else:
        rptmessages=[]
    datas=[bmessages,opmessages,fmessages,cmessages,lrmessages,lpmessages,ltmessages,lchangemessages,lcmessages,rptmessages]
    #multi_subject(datas)
    with open('./ocr/static/basic_data.json','w') as w:
        json.dump(datas,w)
    #alldatas,unmatch_alldata,mdatas=match_datas(datas)
    #allpics=[x[2] for x in alldatas]
    #unrecognized=[x.split('/')[-1] for x in t_names if x not in allpics]
    #data={
    #    'mdata':mdatas,
    #    'unmatched':[x[:-1]+[x[-1].split('/')[-1]] for x in unmatch_alldata],
    #    'unrecognized':[x.split('/')[-1] for x in unrecognized]
    #}
    #with open('./ocr/static/data.json','w') as w:
    #    json.dump(data,w)
def type_test(tname):
    ocr_datas,ocr_shapes=ocr_df([tname])
    for od in ocr_datas[0]:
        lp=min([x[0] for x in od[0]])
        rp=max([x[0] for x in od[0]])
        tp=min([x[1] for x in od[0]])
        bp=max([x[1] for x in od[0]])
        osquare=(rp-lp)*(bp-tp)
        print(osquare,osquare/len(od[1][0]),od[1][0])


if __name__=='__main__':
    #get_datas()
    #type_test('./ocr/static/tmp_license/prove_4_0.jpg')
    a=[1,2]
    print(a[1:2])