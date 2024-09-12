from django.shortcuts import render

def home_view(request, *args, **kwargs):
    user_input = None
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
    return render(request, "home.html", {'user_input': user_input})
