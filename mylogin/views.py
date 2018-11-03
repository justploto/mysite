from django.shortcuts import render , redirect
# Create your views here.
from  .models import User, ConfirmString
from .forms import UserForm , RegisterForm
from django.contrib import sessions
from login import  settings
import  hashlib
import  datetime




def index(request):
    # return HttpResponse('index page！！')
    pass
    return render(request,'login/index.html')


def login(request):
    # return HttpResponse('login page！！')
    # if request.method =='POST':
    #     username = request.POST.get('username',None)
    #     password = request.POST.get('password',None)
    #     message = "用户名密码都不能为空！"
    #     # print (username,password)
    #     user = None
    #     if username and password:
    #         username = username.strip()
    #         try:
    #             user = User.objects.get(name=username)
    #             print(user,user)
    #             if user.password == password:
    #                 return redirect('/hello/')
    #             else:
    #                 message = '密码错误!!'
    #         except:
    #             message = '用户名错误！'
    #             print(message)
    #
    #     return render(request,'login/login.html',{"message":message})
    print(request.session.get('is_login',None))
    if request.session.get('is_login',None):
        print(request.session.get('is_login'))
        return  redirect('/index/')
    if request.method =='POST':
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.get(name=username)
                if not user.has_confirmed:
                    message = '请邮件确认账号注册信息！'
                    return render(request,'login/login.html' , locals())
                if user.password == hash_code(password):
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = '密码错误!!'
            except:
                message = '用户名错误！'

        return render(request,'login/login.html',{"message":message,"login_form":login_form})
    login_form = UserForm()
    return render(request, 'login/login.html',locals())

def logout(request):
    # return HttpResponse('logout page！！')
    if not request.session.get('is_login',None):
        return redirect("/index/")
    else:
        request.session.flush()
    return redirect('/index/')

def register(request):
    if request.method =='POST':
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 !=password2:
                message = '密码不一致!!'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已经存在!!'
                    return render(request, 'login/register.html', locals())

                same_email_user = User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals())

                new_user = User()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()


                code = make_confirm_string(new_user)
                send_email(email, code)

                message = '请前往注册邮箱，进行邮件确认！'
                return render(request, 'login/confirm.html', locals())  # 跳转到等待邮件确认页面。

    register_form = RegisterForm()
    return render(request, 'login/register.html',{"register_form":register_form})

def hello(request):
    # return HttpResponse('logout page！！')
    pass
    return  render(request,'login/hello.html')

def user_confirm(request):
    code =  request.GET.get('code',None)
    message = ''
    try:
        confirm = ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求!'
        return render(request, 'login/confirm.html', locals())

    c_time = confirm.c_time
    print(c_time)
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(seconds = int(settings.EMAIL_VALID_TIME)):
        confirm.user.delete()
        message = '您的邮件已经过期！请重新注册!'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return render(request, 'login/confirm.html', locals())


def hash_code(s, salt='mylogin'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()

def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name,now)
    ConfirmString.objects.create(code = code , user = user,)
    return  code


def send_email(email,code):
    from django.core.mail import  EmailMultiAlternatives
    subject = '欢迎注册xx网址会员'
    text_content = '欢迎注册xx网址会员,欢迎随时交流！'
    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.mysite.com</a>，\
                    这是个测试，专注于Python和Django技术的分享！</p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
    '''.format('127.0.0.1:8000',code, settings.EMAIL_VALID_TIME)

    msg = EmailMultiAlternatives(subject,text_content,settings.EMAIL_HOST_USER,[email])
    msg.attach_alternative(html_content,'text/html')
    msg.send()