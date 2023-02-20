//刷新自动加载
refresh();

//服务端交互
    function ajax_rqs(method, url, msg, doSomething) {
        var xmlhttp;
        if (window.XMLHttpRequest) {
            // IE7+, Firefox, Chrome, Opera, Safari 浏览器执行代码
            xmlhttp = new XMLHttpRequest();
        }
        else {
            // IE6, IE5 浏览器执行代码
            xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
        }
        xmlhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                doSomething(JSON.parse(this.responseText))
                //bs_insert(api_data);
            }return;
        }
        if (method == "post") {
            xmlhttp.open("POST", url, true);
            xmlhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
            xmlhttp.send(msg);
        }
        else if (method=="file"){
          xmlhttp.open("POST", url, true);
          xmlhttp.send(msg);
        }
        else if (method=="get"){
            xmlhttp.open("GET", url, true)
            xmlhttp.send()
        }
        else {console.log('requests type must in "get","post","file"')}
    };
    function upload(ele){
      if (document.getElementsByClassName("loading").length==0){
        var loading = document.createElement("img")
        var win = ele.parentNode
        var success=0
        loading.setAttribute("class","loading")
        loading.setAttribute("src","/static/loading.gif")
        win.appendChild(loading)
        var form = ele
        var eles=form.elements
        var url = "/uploader"
        for (var i=0;i<eles.length;i++){
          if (eles[i].type=="file"){
            //var file_obj = eles[i].files[0]
            var file_objs = eles[i].files
            var nums=file_objs.length
            for (var j=0;j<nums;j++){
              var file_obj = file_objs[j]
              var param = new FormData()
              param.append([eles[i].name],file_obj)
              if (file_obj){
                ajax_rqs("file",url,param,function(data){
                  if(response_render(data)){
                    success+=1;
                    if(document.getElementById("progress")){
                      win.removeChild(document.getElementById("progress"))
                    }
                    var progress_ele=document.createElement("div")
                    var progress_text=document.createTextNode("当前进度:"+String(success)+"/"+String(nums))
                    progress_ele.appendChild(progress_text)
                    progress_ele.setAttribute("id","progress")
                    progress_ele.setAttribute("class","loading")
                    win.appendChild(progress_ele)
                    if (success==nums){
                      close_win('mask');
                      refresh()
                    }
                  }
                })
              }
            }
          }
        }
      }
    }

//弹窗
    function addPic(){
      var parentEle=document.body
      var addWindow = document.createElement("div")
      addWindow.setAttribute("id","mask")
      var win = document.createElement("div")
      win.setAttribute("class","addPicWin")
      win.setAttribute("style","background-color:#FFFFFF;")
      var close_button = document.createElement("button")
      close_button.setAttribute("onclick","close_win('mask')")
      close_button.setAttribute("class","close")
      var closeText = document.createTextNode("关闭")
      close_button.appendChild(closeText)
      win.appendChild(close_button)
      insert_row(win)
      addWindow.appendChild(win)
      parentEle.appendChild(addWindow)
    }
    function close_win(id){
      var mask = document.getElementById(id)
      if (mask){
        document.body.removeChild(mask)
      }
    }
    function insert_row(pele){
        var row_obj = document.createElement("Form")
        row_obj.setAttribute("class","row")
        row_obj.setAttribute("onsubmit","return false")
        var file_ipt = document.createElement("input")
        file_ipt.setAttribute("name","file")
        file_ipt.setAttribute("type","file")
        file_ipt.setAttribute("multiple","multiple")
        var fileText = document.createTextNode("SUBMIT FILE")
        file_ipt.appendChild(fileText)
        row_obj.appendChild(file_ipt)
        var upload_button = document.createElement("button")
        upload_button.setAttribute("onclick","upload(this.parentNode)")
        var bText=document.createTextNode("上传")
        upload_button.appendChild(bText)
        row_obj.appendChild(upload_button)
        pele.appendChild(row_obj)
    };
//添加or删除=刷新--均重新请求文件列表接口
    function refresh(){
      var url1='/refresh'
      ajax_rqs("get",url1,'',function(datas){files_render(datas)})
      //自动加载数据
      get_rawData();
      //cols_render();
      //var url2 = "/refresh_data"
      //ajax_rqs("get",url2,'',function(datas){data_render(datas)})
      //自动识别状态
      process_check();
    }
    function response_render(data){
      if (data['status']=="success"){
        return 1
      }
    }
    function files_render(datas){
      var fns = datas
      var pics_ele=document.getElementById("pics")
      //清空后重新加载
      var ele_childs=pics_ele.children
      for (var j=ele_childs.length-1;j>=0;j--){
        pics_ele.removeChild(ele_childs[j])
      }
      for (var i=0;i<fns.length;i++){
        var pic_ele=document.createElement("div")
        var url = "/static/tmp_license/"+fns[i]
        pic_ele.setAttribute("value",fns[i])
        pic_ele.setAttribute("style","margin-bottom:15px")
        var text=document.createTextNode(fns[i])
        pic_ele.appendChild(text)
        var href_b = document.createElement("button")
        var href_t = document.createTextNode("查看图片")
        href_b.setAttribute("href",url)
        href_b.setAttribute("style","position:absolute;left:50%")
        href_b.setAttribute("onclick","show_pic(this)")
        href_b.appendChild(href_t)
        pic_ele.appendChild(href_b)
        var del_ele = document.createElement("button")
        var del_text=document.createTextNode("删除")
        del_ele.setAttribute("style","position:absolute;left:75%")
        del_ele.setAttribute("onclick","del_ele(this.parentNode)")
        del_ele.appendChild(del_text)
        pic_ele.appendChild(del_ele)
        pics_ele.appendChild(pic_ele)
      }
    }
    function pic_groups(picn,pic_name,td){
      //图片列表
      var piceles=document.getElementById("pics")
      var picseles=piceles.children
      //图片组ID
      var pic_group_ids=[];
      for (var i=0;i<picseles.length;i++){
          var picvalue=picseles[i].getAttribute("value")
          var pvs=picvalue.split('_')
          if (pvs.length==3){
            var pic_gid=pvs[1]
            if (pic_group_ids.indexOf(pic_gid)==-1){
              pic_group_ids.push(pic_gid)
            }
          }
      }
      //图片组数量
      var pic_groups_num=[]
      for (var i=0;i<pic_group_ids.length;i++){
          var cnt=0;
          var pic_group_id=pic_group_ids[i];
          for (var j=0;j<picseles.length;j++){
            var pid=picseles[j].getAttribute("value").split('_')[1]
            if (pic_group_id==pid){
              cnt+=1
            }
          }
          pic_groups_num.push(cnt)
      }
      //目标图片
      var picns=picn.split("_")
      var gid;
      if (picns.length==3){
        gid=picns[1]
        var idx=pic_group_ids.indexOf(gid)
        var glength=pic_groups_num[idx]
        for (var i=0;i<glength;i++){
          var btn=document.createElement("button")
          var text=pic_name+"_"+String(i)
          if (picn==pic_name || pic_name==""){
            text=picn.split("_0")[0]+"_"+String(i)+".jpg"
          }
          var fname="prove_"+gid+"_"+i+".jpg"
          var btnt=document.createTextNode(text)
          btn.setAttribute("href","/static/tmp_license/"+fname)
          btn.setAttribute("onclick","show_pic(this)")
          btn.setAttribute("class","table_button")
          btn.appendChild(btnt)
          td.appendChild(btn)
        }
        var br=document.createElement("br")
        td.appendChild(br)
        }
      else{
        var btn=document.createElement("button")
        var btnt=document.createTextNode(picn)
        btn.setAttribute("href","/static/tmp_license/"+picn)
        btn.setAttribute("onclick","show_pic(this)")
        btn.setAttribute("class","table_button")
        btn.appendChild(btnt)
        td.appendChild(btn)          
      }        
    }

    function show_pic(ele){
      var url = ele.getAttribute("href")
      var parentEle=document.body
      var addWindow = document.createElement("div")
      addWindow.setAttribute("id","mask")
      addWindow.setAttribute("onclick","close_win('mask')")
      var win = document.createElement("img")
      win.setAttribute("src",url)
      win.setAttribute("class","obverse_win")
      addWindow.appendChild(win)
      parentEle.appendChild(addWindow)
    }

    function show_pics(ele){
      var url = ele.getAttribute("href")
      var plist = document.getElementById("pics").children
      var pnames = []
      for (var i=0;i<plist.length;i++){
        pnames.push(plist[i].getAttribute("value"))
      }
      var url_psplits = url.split("/")
      var urlpns=url_psplits[url_psplits.length-1].split("_")
      var urls=[]
      if(urlpns.length==2){
        urls=[url.replace("./ocr","")]
      }
      else if(urlpns.length==3){
        var urlb=urlpns[0]+"_"+urlpns[1]
        for(var i=0;i<plist.length;i++){
          var url_c=urlb+"_"+i+".jpg"
          if(pnames.indexOf(url_c)!=-1){
            urls.push("/static/tmp_license/"+url_c)
          }
        }
      }
      var parentEle=document.body
      var addWindow = document.createElement("div")
      addWindow.setAttribute("id","mask")
      addWindow.setAttribute("onclick","close_win('mask')")
      for(var i=0;i<urls.length;i++){
        var win = document.createElement("img")
        win.setAttribute("src",urls[i])
        win.setAttribute("class","obverse_win")
        addWindow.appendChild(win)
        parentEle.appendChild(addWindow)
      }
    }



    function del_all(){
      var url = '/del_all'
      ajax_rqs("get",url,'',function(data){
        if (data['status']=="success"){
          refresh()
        }
      })
    }
    function del_ele(ele){
      var value = ele.getAttribute("value")
      url = "/del_pic?value="+value
      ajax_rqs("get",url,'',function(data){
        if (data['status']=="success"){
          refresh()
        }
      })
    }
//数据加载蒙版
    function process_check(){
      var url = "/process_status"
      //var status=true
      var btn=document.getElementById("bpd")
      btn.setAttribute("disable","true")
      var mask = document.createElement("div")
      mask.setAttribute("id","mask")
      var loading = document.createElement("img")
      loading.setAttribute("class","loading")
      loading.setAttribute("src","/static/loading.gif")
      mask.appendChild(loading)
      document.body.appendChild(mask)
      var mask_h = document.getElementById("mask")
      if (mask_h){
        function get_status(){
          ajax_rqs("get",url,'',function(data){
            if (data["status"]=="success"){
              btn.setAttribute("disable","false")
              document.body.removeChild(mask_h)
            }
            else{
              setTimeout(function(){
                get_status();
              },2000)
            }
          })
        }
        get_status();
      }
    }

    function multi_produce(){
      var url = "/multi_produce"
      ajax_rqs("get",url,'',function(data){console.log(data)})
      refresh()
    }

    /*
    function cols_render(){
      var tab0=document.getElementById("tab0")
      var tab1=document.getElementById("tab1")
      var tab2=document.getElementById("tab2")
      var thr0=document.createElement("tr")
      var thr1=document.createElement("tr")
      var thr2=document.createElement("tr")
      var t0_cols=["营业执照及期限","经营许可及期限","承诺函","生产许可及期限","商标授权","质检报告"]
      
      //清空重新加载表格
      var tab0rs = tab0.children
      var tab1rs = tab1.children
      var tab2rs = tab2.children
      for (var i=tab0rs.length-1;i>=0;i--){
        tab0.removeChild(tab0rs[i])
      }
      for (var i=tab1rs.length-1;i>=0;i--){
        tab1.removeChild(tab1rs[i])
      }
      for (var i=tab2rs.length-1;i>=0;i--){
        tab2.removeChild(tab2rs[i])
      }

      for(var i=0;i<t0_cols.length;i++){
        var thd = document.createElement("th")
        var text = document.createTextNode(t0_cols[i])
        thd.appendChild(text)
        thr0.appendChild(thd) 
      }
      tab0.appendChild(thr0)
      var t1_cols=["图片","资质类型","所属机构及ID","操作"]
      for(var i=0;i<t1_cols.length;i++){
        var thd = document.createElement("th")
        var text = document.createTextNode(t1_cols[i])
        thd.appendChild(text)
        thr1.appendChild(thd)
      }
      tab1.appendChild(thr1)
      var t2_cols=["图片","操作"]
      for(var i=0;i<t2_cols.length;i++){
        var thd = document.createElement("th")
        var text = document.createTextNode(t2_cols[i])
        thd.appendChild(text)
        thr2.appendChild(thd) 
      }
      tab2.appendChild(thr2)
    }
    function data_render(datas){
      var tab0=document.getElementById("tab0")
      var tab1=document.getElementById("tab1")
      var tab2=document.getElementById("tab2")
      if(datas){
        var mdatas = datas["mdata"]
        var unmatched = datas["unmatched"]
        var unrecognized = datas["unrecognized"]
      }
      else{
        var mdatas=[]
        var unmatched=[]
        var unrecognized=[]
      }
      for (var i=0;i<mdatas.length;i++){
        var tr=document.createElement("tr")
        //营业执照
        var bn=document.createElement("td")
        if (mdatas[i]["bname"]!=""){
          var bnd=document.createElement("button")
          var bnt=document.createTextNode(mdatas[i]["bname"])
          bnd.setAttribute("href","/static/tmp_license/"+mdatas[i]["bf"])
          bnd.setAttribute("onclick","show_pic(this)")
          bnd.setAttribute("class","table_button")
          bnd.appendChild(bnt)
          bn.appendChild(bnd)
        }
        tr.appendChild(bn)
        //经营许可
        var opn=document.createElement("td")
        if (mdatas[i]["opf"]!=""){
          var opnd=document.createElement("button")
          var opnt=document.createTextNode(mdatas[i]["opf"])
          opnd.setAttribute("href","/static/tmp_license/"+mdatas[i]["opf"])
          opnd.setAttribute("onclick","show_pic(this)")
          opnd.setAttribute("class","table_button")
          opnd.appendChild(opnt)
          opn.appendChild(opnd)
        }
        tr.appendChild(opn)
        //承诺函
        var cn=document.createElement("td")
        if (mdatas[i]["cf"]!=""){
          var cnb=document.createElement("button")
          var cnt=document.createTextNode("查看图片")
          cnb.setAttribute("href","/static/tmp_license/"+mdatas[i]["cf"])
          cnb.setAttribute("onclick","show_pic(this)")
          cnb.setAttribute("class","table_button")
          cnb.appendChild(cnt)
          cn.appendChild(cnb)
        }
        tr.appendChild(cn)
        //生产许可
        var fn=document.createElement("td")
        if (+mdatas[i]["pf"]!=""){
          var fnd=document.createElement("button")
          var fnt=document.createTextNode(mdatas[i]["fname"])
          fnd.setAttribute("href","/static/tmp_license/"+mdatas[i]["pf"])
          fnd.setAttribute("onclick","show_pic(this)")
          fnd.setAttribute("class","table_button")
          fnd.appendChild(fnt)
          fn.appendChild(fnd) 
        }
        tr.appendChild(fn)
        //商标授权
        var ln=document.createElement("td")
        var labels=mdatas[i]["brand_fs"]
        for (var j=0;j<labels.length;j++){
          pic_groups(labels[j],labels[j],ln)
        }
        tr.appendChild(ln)        
        //质检报告
        var rptn=document.createElement("td")
        var rpts=mdatas[i]["brpts_fs"]
        var r_names=mdatas[i]["pns"]
        for (var j=0;j<rpts.length;j++){
          pic_groups(rpts[j],r_names[j],rptn)
        }
        tr.appendChild(rptn)
        //插入表格
        tab0.appendChild(tr)
      }
      for (var i=0;i<unmatched.length;i++){
        var tr = document.createElement("tr")
        //图片
        var ptd = document.createElement("td")
        var pic = unmatched[i][2]
        //var text = unmatched[i][1][1]
        pic_groups(pic,pic,ptd)
        tr.appendChild(ptd)
        //类型
        var ttd = document.createElement("td")
        var ttdbt = document.createTextNode(unmatched[i][0])
        ttd.appendChild(ttdbt)
        tr.appendChild(ttd)
        //名称
        var ntd = document.createElement("td")
        var ntdtx = unmatched[i][1].join("_")
        var ntdbt = document.createTextNode(ntdtx)
        ntd.appendChild(ntdbt)
        tr.appendChild(ntd)
        //操作
        var optd = document.createElement("td")
        
        tr.appendChild(optd)
        //插入表格
        tab1.appendChild(tr)
      }
      for (var i=0;i<unrecognized.length;i++){
        var tr = document.createElement("tr")
        var td = document.createElement("td")
        pic_groups(unrecognized[i],unrecognized[i],td)
        tr.appendChild(td)
        //操作
        var optd = document.createElement("td")
        
        tr.appendChild(optd)
        tab2.appendChild(tr)
      }
    }
    */
    

    function get_rawData(){
      //ajax_rqs("get","/raw_data",'',function(data){fe_produce(data)})
      ajax_rqs("get","/refresh_data",'',function(data){exist_data(data)})
      //refresh()
    }
    

    function exist_data(data){
      var datas=data["data"]
      var unmatch=data["unmatch"]
      if(datas){
        var tab_ele=document.getElementById("tab0")
        var roweles=tab_ele.children
        for(var i=roweles.length-1;i>=0;i--){
          tab_ele.removeChild(roweles[i])
        }
        var um_ele=document.getElementById("tab2")
        var umrs=um_ele.children
        for(var i=umrs.length-1;i>=0;i--){
          um_ele.removeChild(umrs[i])
        }
        var msg_types = ["营业执照","经营许可","生产许可","承诺函","商标注册","商标授权","商标转让","商标变更","商标续展","检验报告"]
        msg_types.push("操作")
        var thr=document.createElement("tr")
        var tidhd=document.createElement("th")
        tidhd.appendChild(document.createTextNode("序号"))
        thr.appendChild(tidhd)
        for(var i=0;i<msg_types.length;i++){
          var thd=document.createElement("th")
          thd.appendChild(document.createTextNode(msg_types[i]))
          thr.appendChild(thd)
        }
        tab_ele.appendChild(thr)
          
        var unmnames=["资质图片","操作"]
        var uthr=document.createElement("tr")
        var uthd1=document.createElement("th")
        var uthdt1=document.createTextNode(unmnames[0])
        uthd1.appendChild(uthdt1)
        uthr.appendChild(uthd1)
        var uthd2=document.createElement("th")
        var uthdt2=document.createTextNode(unmnames[1])
        uthd2.appendChild(uthdt2)
        uthr.appendChild(uthd2)
        um_ele.appendChild(uthr)
  
        for(var i=0;i<datas.length;i++){
          var tr_ele=document.createElement("tr")
          var idxTD=document.createElement("td")
          var idx=document.createTextNode(i+1)
          idxTD.appendChild(idx)
          tr_ele.appendChild(idxTD)
          var r_data=datas[i]
          for(var j=0;j<r_data.length;j++){
            var c_data=r_data[j]
            var td_ele=document.createElement("td")
            for(var k=0;k<c_data.length;k++){
              var item=c_data[k]
              var item_div=document.createElement("button")
              var item_text=document.createTextNode(item[0])
              item_div.setAttribute("href","/static/tmp_license/"+item[1])
              item_div.setAttribute("onclick","show_pics(this)")
              item_div.setAttribute("class","table_button")
              item_div.appendChild(item_text)
              td_ele.appendChild(item_div)
            }
            tr_ele.appendChild(td_ele)
          }
          var m_td=document.createElement("td")
          mtd(m_td,datas.length,i)
          tr_ele.appendChild(m_td)
          tab_ele.appendChild(tr_ele)
        }
        for(var i=0;i<unmatch.length;i++){
          var utr=document.createElement("tr")
          var utd=document.createElement("td")
          var udiv=document.createElement("div")
          var utext=document.createTextNode(unmatch[i][0])
          udiv.setAttribute("href",unmatch[i][1])
          udiv.appendChild(utext)
          utd.appendChild(udiv)
          utr.appendChild(utd)
          var um_td=document.createElement("td")
          mtd(um_td,datas.length,0)
          utr.appendChild(um_td)
          tab_ele.appendChild(utr)
        }
      }
      else{
        ajax_rqs("get","/raw_data",'',function(data){fe_produce(data)})
      }
    }

    function fe_produce(data){
      //console.log(data[0])
      var unmatchdata = data[1]
      var matchdata = data[0]
      //console.log(matchdata)
      var msg_types = ["营业执照","经营许可","生产许可","承诺函","商标注册","商标授权","商标转让","商标变更","商标续展","检验报告"]
      //所有资质主体
      var sub_names=[]
      for(var i=0;i<matchdata.length;i++){
        var tdatas=matchdata[i]
        for(var j=0;j<tdatas.length;j++){  
          if(i!=5 && i!=4){
            var sub_n=tdatas[j][1][0]
            if(sub_names.indexOf(sub_n)==-1){
              sub_names.push(sub_n)
            }
          }
          else if(i==4){
            var sub_n=tdatas[j][1][1]
            if(sub_names.indexOf(sub_n)==-1){
              sub_names.push(sub_n)
            }
          }
          else{
            var sub_n0=tdatas[j][1][0]
            if(sub_names.indexOf(sub_n0)==-1){
              sub_names.push(sub_n0)
            }
            var sub_n1=tdatas[j][1][1]
            if(sub_names.indexOf(sub_n1)==-1){
              sub_names.push(sub_n1)
            }
          }
        }
      }
      
      var lr_datas=matchdata[5]
      var permit_groups=[]
      var sub_include=[]
      
      for (var i=0;i<lr_datas.length;i++){
        //关联主体初始化
        var lr_subs=[lr_datas[i][1][0],lr_datas[i][1][1]]
        //遍历其他关联主体0位,加入关联1位数据
        for(var j=0;j<lr_datas.length;j++){
          var sub_msgs=lr_datas[j][1]
          if(lr_subs.indexOf(sub_msgs[1])==-1 && lr_subs.indexOf(sub_msgs[0])!=-1){
            lr_subs.push(sub_msgs[1])
            //关联数据加入已关联列表
            if(sub_include.indexOf(sub_msgs[1])==-1){
              sub_include.push(sub_msgs[1])
            }
          }
        }
        //遍历其他关联主体1位,计入关联0位数据
        for(var j=0;j<lr_datas.length;j++){
          var sub_msgs=lr_datas[j][1]
          if(lr_subs.indexOf(sub_msgs[1])!=-1 && lr_subs.indexOf(sub_msgs[0])==-1){
            lr_subs.push(sub_msgs[0])
            //关联数据加入已关联列表
            if(sub_include.indexOf(sub_msgs[0])==-1){
              sub_include.push(sub_msgs[0])
            }
          }
        }
        permit_groups.push(lr_subs)
      }

      var pgs=[]
      //合并关联主体
      for(var k=0;k<permit_groups.length;k++){
        var pg=permit_groups[k]
        for(var l=0;l<pg.length;l++){
          for(var o=0;o<permit_groups.length;o++){
            if(permit_groups[o].indexOf(pg[l])!=-1){
              if(permit_groups[o].length>=pg.length){
                pg=permit_groups[o]
              }
            }
          }
          break
        }
        if(pgs.indexOf(pg)==-1){
          pgs.push(pg)
        }
      }
      //合并未关联主体
      for (var i=0;i<sub_names.length;i++){
        if(sub_include.indexOf(sub_names[i])==-1){
          pgs.push([sub_names[i]])
        }
      }

      var mdata=data[0]
      //var mdata=[test_data]
      var group_data=[]
      for(var i=0;i<pgs.length;i++){
        var pgt_data=[]
        for(var j=0;j<mdata.length;j++){
          var ldata=mdata[j]
          var pg_data=[]
          for (var k=0;k<ldata.length;k++){
            if((pgs[i].indexOf(ldata[k][1][0])!=-1)||(pgs[i].indexOf(ldata[k][1][1])!=-1 && (j==5 || j==4))){
              pg_data.push(ldata[k])
            }
          }
          pgt_data.push(pg_data)
        }
        group_data.push(pgt_data)
        //console.log(pgs[i],pgt_data)
      }
      //调用渲染页面数据方法
      fe_render(msg_types,group_data,unmatchdata)
    }

    function fe_render(msg_types,group_data,unmatchdata){
      msg_types.push("操作")
      var tab=document.getElementById("tab0");
      var tab_um=document.getElementById("tab2");
      var tab_rs=tab.children
      var tabu_rs=tab_um.children
      for (var i=tab_rs.length-1;i>=0;i--){
        tab.removeChild(tab_rs[i])
      }
      for (var i=tabu_rs.length-1;i>=0;i--){
        tab_um.removeChild(tabu_rs[i])
      }
      var thr_ele=document.createElement("tr")
      var thi_ele=document.createElement("th")
      var thi_text=document.createTextNode("序号")
      thi_ele.appendChild(thi_text)
      thr_ele.appendChild(thi_ele)
      for (var i=0;i<msg_types.length;i++){
        var th_ele=document.createElement("th")
        var th_text=document.createTextNode(msg_types[i])
        th_ele.appendChild(th_text)
        thr_ele.appendChild(th_ele)
      }
      tab.appendChild(thr_ele)
      for (var i=0;i<group_data.length;i++){
        var tr_ele=document.createElement("tr")
        var idxTD=document.createElement("td")
        var idx=document.createTextNode(i+1)
        idxTD.appendChild(idx)
        tr_ele.appendChild(idxTD)
        for (var j=0;j<msg_types.length;j++){
          var td_objs=group_data[i][j]
          var td=document.createElement("td")
          if(j==msg_types.length-1){
            mtd(td,group_data.length,i)
          }
          else{
            if(td_objs.length>0){
              for(var k=0;k<td_objs.length;k++){
                var url = td_objs[k][2].replace(".ocr/","static/tmp_license/")
                var tdiv=document.createElement("button")
                var tdivt=document.createTextNode(td_objs[k][1].join("_"))
                tdiv.setAttribute("href",url)
                tdiv.setAttribute("onclick","show_pics(this)")
                tdiv.setAttribute("class","table_button")
                tdiv.appendChild(tdivt)
                td.appendChild(tdiv)
              }
            }
          }
          tr_ele.appendChild(td)
        }
        tab.appendChild(tr_ele)
      }

      var unmnames=["资质图片","操作"]
      var uthr=document.createElement("tr")
      var uthd1=document.createElement("th")
      var uthdt1=document.createTextNode(unmnames[0])
      uthd1.appendChild(uthdt1)
      uthr.appendChild(uthd1)
      var uthd2=document.createElement("th")
      var uthdt2=document.createTextNode(unmnames[1])
      uthd2.appendChild(uthdt2)
      uthr.appendChild(uthd2)
      tab_um.appendChild(uthr)

      for (var i=0;i<unmatchdata.length;i++){
        var utr=document.createElement("tr")
        var utdp=document.createElement("td")
        var utdpt=document.createTextNode(unmatchdata[i])
        utdp.setAttribute("href","static/tmp_license/"+unmatchdata[i])
        utdp.appendChild(utdpt)
        utr.appendChild(utdp)
        var utda = document.createElement("td")
        mtd(utda,group_data.length,"u")
        utr.appendChild(utda)
        tab_um.appendChild(utr)
      }
    }
    
    function mtd(td,l,c){
      var slt = document.createElement("select")
      for (var i=0;i<l;i++){
        var opt = document.createElement("option")
        var optt = document.createTextNode(i+1)
        if (i==c){
          opt.selected=true
        }
        opt.appendChild(optt)
        slt.appendChild(opt)
      }
      td.appendChild(slt)
      if (c=="u"){
        var ts=["营业执照","经营许可","生产许可","承诺函","商标注册","商标授权","商标转让","商标变更","商标续展","检验报告"]
        var slt1 = document.createElement("select")
        for (var i=0;i<ts.length;i++){
          var opt_t = document.createElement("option")
          var optt_t = document.createTextNode(i+1)
          opt_t.appendChild(optt_t)
          slt1.appendChild(opt_t)
        }
        td.appendChild(slt1)
      }
      var b = document.createElement("button")
      var bt = document.createTextNode("匹配")
      b.setAttribute("onclick","match_row(this)")
      b.appendChild(bt)
      td.appendChild(b)
    }

    function match_row(ele){
      var td=ele.parentNode
      var value=td.children[0].selectedIndex+1
      var tab = document.getElementById("tab0")
      var trs = tab.children
      for (var i=1;i<trs.length;i++){
        var tds=trs[i].children
        var tdms=trs[value].children
        var tdf=tds[tds.length-1]
        if (td==tdf && value!=i){
          for (var j=1;j<tds.length-1;j++){
            var btns=tds[j].children
            if(btns.length!=0){
              for(var k=0;k<btns.length;k++){
                var btn=btns[k].cloneNode(true)
                tdms[j].appendChild(btn)
              }
              for(var k=btns.length-1;k>=0;k--){
                tds[j].removeChild(btns[k])
              }
            }
          }
          break
        }
      }
    }

    function clear_sync(){
      var new_datas = JSON.stringify({})
      var url = "/data_update"
      ajax_rqs("post",url,new_datas,function(data){response_render(data)})
    }

    function sync_tab(){
      var tab = document.getElementById("tab0")
      var trs = tab.children
      var datas=[]
      var trl=trs.length-1
      for(var i=1;i<trs.length;i++){
        var tds=trs[i].children
        var row=[]
        var if_emp=true
        for(var j=1;j<tds.length-1;j++){
          var tdc=tds[j].children
          var td_data=[]
          for(var k=0;k<tdc.length;k++){
            var inf=[tdc[k].innerHTML,tdc[k].getAttribute("href").replace("./ocr/static/tmp_license/","")]
            td_data.push(inf)
          }
          if(td_data.length>0){
            if_emp=false
          }
          row.push(td_data)
        }
        if(!if_emp){
          datas.push(row)
        }
      }
      for (var i=trs.length-1;i>=1;i--){
        var if_emp=true
        for(var j=1;j<trs[i].children.length-1;j++){
          if(trs[i].children[j].children.length>0){
            if_emp=false
            break
          }
        }
        if(if_emp){
          tab.removeChild(trs[i])
          trl-=1
        }
      }
      var new_trs=document.getElementById("tab0").children
      for(var i=1;i<new_trs.length;i++){
        new_trs[i].children[0].innerHTML=i
        var new_tl=new_trs[i].children.length
        var select_ele=new_trs[i].children[new_tl-1].children[0]
        select_ele.children[i-1].selected=true
        for(var j=select_ele.children.length-1;j>=trl;j--){
          select_ele.removeChild(select_ele.children[j])
        }
      }
      var unmatch_trs=document.getElementById("tab2").children
      var unmatch=[]
      for (var i=1;i<unmatch_trs.length;i++){
        var picn=unmatch_trs.children[0].getAttribute("href")
        unmatch.push(picn.replace("./ocr/static/tmp_license/",""))
      }

      //服务端同步数据
      var new_datas = JSON.stringify({"data":datas,"unmatch":unmatch})
      var url = "/data_update"
      ajax_rqs("post",url,new_datas,function(data){response_render(data)})
    }