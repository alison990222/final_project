from django.shortcuts import render, redirect

from .forms import RegisterForm


def register(request):
    # get the "next" parameter from POST or GET
    # GET: "next" is passed by url -> /?next=value
    # POST: "next" is passed by form -> <input type="hidden" name="next" value="{{ next }}"/>
    # "next" will record the previous visiting page, and then redirect back after registration
    redirect_to = request.POST.get('next', request.GET.get('next', ''))

    if request.method == 'POST':
        # submit username and password
        # 實例化一個用戶註冊表單
        form = RegisterForm(request.POST)

        if form.is_valid():
            # if the form is valid, save it
            # django 自己的包
            form.save()

            if redirect_to:
                return redirect(redirect_to)
            else:
                return redirect('/')
    else:
        # if request is not POST, it indicates that the user is visiting register page.
        # so show an empty register form
        form = RegisterForm()

    return render(request, 'users/register.html', context={'form': form, 'next': redirect_to})


def index(request):
    return render(request, 'index.html')
