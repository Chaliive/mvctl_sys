#!/usr/bin/env python3
from flask import Flask, request
from flask import render_template
import libvirt,os
import random
import pymysql
app = Flask(__name__)
db = pymysql.connect(host='127.0.0.1', user='root', password='', db='test', port=3306)
current_user = ['登录']
cur = db.cursor()
conn = libvirt.open("qemu+tcp://192.168.73.144/system")
info = conn.getInfo()
#xml = open("/etc/libvirt/qemu/centos7-template.xml").read()

def show_vm():
    vms_dict = {}
    domain_list = conn.listDomainsID()
    for vm in domain_list:
        vms_dict[vm]=conn.lookupByID(vm).name()
    return vms_dict

def show_down_vm():
    vmd_list = []
    for i in conn.listDefinedDomains():
        vmd_list.append(i)
    return vmd_list

def temp(name):
    f = open('/etc/libvirt/qemu/{}.xml'.format(name))
    xml = f.read()
    try:
        conn.createXML(xml)
        return "临时开启成功"
    except:
        return "临时开启失败，请检查输入的虚拟机是否存在"
    finally:
        f.close()
#print(temp('centos7_2'))


def suspand(vmname):
    dom = conn.lookupByName(vmname)
    try:
        dom.suspend()
        return "suspend successful"
    except:
        return "suspend failed"


def create(vmname):
    try:
        num = random.randint(10000,99999)  # 产生随机数，用于uuid
    #    print(num)
        file = open("/etc/libvirt/qemu/centos-template.xml")
        xml = file.read()
        xml_new = open("/etc/libvirt/qemu/{}.xml".format(vmname),"w")
        str1 = xml.replace("<name>none</name>","<name>{}</name>".format(vmname))
        str2 = str1.replace("<uuid>none</uuid>","<uuid>029b94d0-652b-4414-91ca-4212801{}</uuid>".format(num))
        #str2 = str1.replace("<source file='/root/KVM_2.qcow2'/>","<source file='/root/{}.qcow2'/>".format(vmname))
        #os.popen("cp /root/KVM_2.qcow2 /root/{}.qcow2".format(vmname)).readlines()
        print(str2)
        xml_new.write(str2)
        conn.defineXML(str2)
        file.close()
        xml_new.close()
        return "创建成功"
    except:
        return "创建失败，请检查输入的名字是否已存在"


def shutdown(vmname):
    try:
        dom = conn.lookupByName(vmname)
        dom.shutdown()
        msg = "{}关闭成功".format(vmname)
        return msg
    except:
        msg = "{}关闭失败".format(vmname)
        return msg


def destroy(vmname):
    try:
        dom = conn.lookupByName(vmname)
        dom.destroy()
        msg = "{}关闭成功".format(vmname)
        return msg
    except:
        msg = "{}关闭失败,请检查{}是否开启".format(vmname,vmname)
        return msg

#vms = show_vm()
#vmd = show_down_vm()

@app.route('/regist')
def regist():
    return render_template('regist.html', user=current_user[-1])


@app.route('/regist', methods=['POST'])
def regist_post():
    nickname = request.form['username']
    rename = """
    select * from regist where nickname='%s'
    """
    n = cur.execute(rename % nickname)
    db.commit()
    if n > 0:
        return render_template('regist.html', registerr="该昵称已被使用")
    else:
        password = request.form['pwd']
        email = request.form['email']
        phone = request.form['tel']
        sql_insert = """
    insert into regist values('%s','%s','%s','%s')
    """
        cur.execute(sql_insert % (nickname, password, email, phone))
        db.commit()
        return render_template('login.html', user=current_user[-1])


@app.route('/', methods=['GET'])
def login():
    return render_template('login.html', user=current_user[-1])


@app.route('/login', methods=['POST'])
def login_form():
    sql_select = """
select nickname,password from regist
"""
    cur.execute(sql_select)
    db.commit()
    results = cur.fetchall()
    vms = show_vm()
    vmd = show_down_vm()
    for row in results:
        if request.form['username'] == row[0] and request.form['pwd'] == row[1]:
            username = request.form['username']
            current_user.append(username)
         #   info = memory()
         #   sys_result = get_data()
         #   pro_res = process()
         #   disk_info = disk()
         #   for k, v in disk_info.items():
         #       ks, vs = k, v
            return render_template('kvm.html',info=info,vms=vms,vmd=vmd)
    return render_template('login.html', mess='用户名或密码不正确', user=current_user[-1])



@app.route('/abc', methods=['GET'])
def kvm():
    vms = show_vm()
    vmd = show_down_vm()
    return render_template('kvm.html',info=info,vms=vms,vmd=vmd)


@app.route('/kvm',methods=['POST'])
def vm_get():
    vmname = request.form['vmname']
    msg = temp(vmname)
    vms = show_vm()
    vmd = show_down_vm()
    return render_template('kvm.html',msg=msg,info=info,vms=vms,vmd=vmd)


@app.route('/suspand',methods=['POST'])
def vm_suspand():
    vmname = request.form['vmname2']
    msg2 = suspand(vmname)
    vms = show_vm()
    vmd = show_down_vm()
    return render_template('kvm.html',msg2=msg2,info=info,vms=vms,vmd=vmd)


@app.route('/create',methods=['POST'])
def vm_create():
    vmname = request.form['vmname3']
    msg3 = create(vmname)
    vms = show_vm()
    vmd = show_down_vm()
    return render_template('kvm.html',msg3=msg3,info=info,vms=vms,vmd=vmd)


@app.route('/shutdown',methods=['POST'])
def vm_shutdown():
    vmname = request.form['vmname4']
    msg4 = shutdown(vmname)
    vms = show_vm()
    vmd = show_down_vm()
    return render_template('kvm.html',msg4=msg4,info=info,vms=vms,vmd=vmd)


@app.route('/destroy',methods=['POST'])
def vm_destroy():
    vmname = request.form['vmname5']
    msg5 = destroy(vmname)
    vms = show_vm()
    vmd = show_down_vm()
    return render_template('kvm.html',msg5=msg5,info=info,vms=vms,vmd=vmd)


@app.route('/pqz',methods=["POST"])
def qz_post():
    vmname = request.form['vmname6']
    a=os.popen("virsh snapshot-create {}".format(vmname))
    list = []
    vms = show_vm()
    vmd = show_down_vm()
    for i in a:
        return render_template('kvm.html',message='拍摄快照成功，{}'.format(i),info=info,vms=vms,vmd=vmd)


@app.route('/hfqz',methods=["POST"])
def hfqz_post():
    name=request.form['vmname7']
    os.popen("virsh snapshot-revert {}".format(name))
    vms = show_vm()
    vmd = show_down_vm()
    return render_template('kvm.html',message='快照已恢复',info=info,vms=vms,vmd=vmd)


if __name__ == '__main__':
    app.run(host='192.168.73.144', port=888, debug=True)



