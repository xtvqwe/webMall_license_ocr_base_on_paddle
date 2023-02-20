import pdf2image
import gc
import os

def pdf_cvt(fname):
    pages=pdf2image.convert_from_path(fname,500)
    fn=fname.split('.pdf')[0]
    pnames=[]
    for pid_0 in range(-len(pages),0):
        pid=-pid_0-1
        pname=fn+'_'+str(pid)+'.jpg'
        pages[pid].save(pname,'JPEG')
        pnames.append(pname)
        del pages[pid]
        gc.collect()
    os.remove(fname)
    gc.collect()
    return pnames

def file_rename(fn):
    fname=fn.split('/')[-1]
    #print(fn)
    path=os.path.dirname(os.path.abspath(__file__))
    fns=[x for x in os.listdir(path+'/static/tmp_license/') if 'prove_' in x]
    if len(fns)==0:
        new_idx=0
    else:
        new_idx=max([int(x.split('_')[1].split('.')[0]) for x in fns])+1
    #print(new_idx)
    names=[]
    if fn[-4:] in['.jpg','.png','.pdf']:
        new_name=path+'/static/tmp_license/prove_'+str(new_idx)+fn[-4:]
        fnn=path+'/static/tmp_license/\"'+fname+'\"'
        os.system('mv '+fnn+' '+new_name)
        if fn[-4:]=='.pdf':
            names=pdf_cvt(new_name)
        else:
            names=[new_name]
    return names
