from django.shortcuts import render, redirect
from django.http import HttpResponse
# Import the Category model
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User



# def index(request):
#     # Query the databse for a list of ALL categories currently stored  
#     # Order the categories by the number of likes in descending order.
#     # Retrieve the top 5 only -- or all if less than 5.
#     # Place the list in our context_dict dictionary (with our boldmessage!)
#     # that will be passed to the template engine.
#     category_list = Category.objects.order_by('-likes')[:5]
#     page_list = Page.objects.order_by('-views')[:5]

#     context_dict = {}
#     # Construct a dictionary to pass to the template engine as its context.
#     # Note the key boldmessage matches to {{ boldmessage }} in the template!
#     context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
#     context_dict['categories'] = category_list
#     context_dict['pages'] = page_list
 
#     # Call the helper function to handle the cookies
#     visitor_cookie_handler(request)

#     # Obtain our Response object eraly so we can add cookie information
#     response = render(request, 'rango/index.html', context=context_dict)
#     # Return response back to the user, updating any cookies that need changed 
#     return response

class IndexView(View):
    def get(self, request):
        category_list = Category.objects.order_by('-likes')[:5]
        page_list = Page.objects.order_by('-views')[:5]

        context_dict = {}
        context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
        context_dict['categories'] = category_list
        context_dict['pages'] = page_list
        context_dict['extra'] = 'From the model solution on GitHub'
        
        visitor_cookie_handler(request)

        return render(request, 'rango/index.html', context=context_dict)


# def about(request):
#     context_dict = {'boldmessage': 'This tutorial has been put together by Greta'}
#     visitor_cookie_handler(request)
#     context_dict['visits'] = request.session['visits']
#     return render(request, 'rango/about.html', context=context_dict)
#     # return HttpResponse("Rango says here is the about page. <a href='/rango/'>Index</a>")

class AboutView(View):
    def get(self, request):
        context_dict = {}

        visitor_cookie_handler(request)
        context_dict['visits'] = request.session['visits']

        return render(request, 'rango/about.html', context_dict)




# def show_category(request, category_name_slug):
#     # Create a context doctionary which we can pass to the template render engine.
#     context_dict = {}

#     try:
#         # Can we find a category name slug with the given name?
#         # If we can't, the .get() method raises a DoesNotExist exception.
#         # The .get() method returns one model instrance or raises an exception.
#         category = Category.objects.get(slug=category_name_slug)

#         # Retrieve all of the associated pages.
#         # The filter() will return a list of page objects or an empty list.
#         pages = Page.objects.filter(category=category).order_by('-views')

#         # Adds our results list to the template context under name pages.
#         context_dict['pages'] = pages
#         # We also add the category objects from the database to the context dictionary.
#         # We'll use this in the template to verify that te category exists.
#         context_dict['category'] = category
#     except Category.DoesNotExist:
#         # We get here if we didn't find the specified category.
#         # Don't do anything - the template will dasplay the "no category" message.
#         context_dict['category'] = None
#         context_dict['pages'] = None

#     # Start new search functionality code.
#     if request.method == 'POST':
#         if request.method == 'POST':
#             query = request.POST['query'].strip()

#             if query:
#                 context_dict['result_list'] = run_query(query)
#                 context_dict['query'] = query
#     # End new search functionlity code.

#     # Go render the response and return it to the client.
#     return render(request, 'rango/category.html', context_dict)

class ShowCategoryView(View):
    def create_context_dict(self, category_name_slug):
        """
        A helper method that was created to demonstarte the power of class-based views.
        You can reuse this method in the get() and post() methods!
        """
        context_dict = {}

        try:
            category = Category.objects.get(slug=category_name_slug)
            pages = Page.objects.filter(category=category).order_by('-views')

            context_dict['pages'] = pages
            context_dict['category'] = category
        except Category.DoesNotExist:
            context_dict['pages'] = None
            context_dict['category'] = None
        
        return context_dict
    
    def get(self, request, category_name_slug):
        context_dict = self.create_context_dict(category_name_slug)
        return render(request, 'rango/category.html', context_dict)
    
    @method_decorator(login_required)
    def post(self, request, category_name_slug):
        context_dict = self.create_context_dict(category_name_slug)
        query = request.POST['query'].strip()

        if query:
            context_dict['result_list'] = run_query(query)
            context_dict['query'] = query
        
        return render(request, 'rango/category.html', context_dict)

# @login_required
# def add_category(request):
#     form = CategoryForm()

#     # A HTTP POST?
#     if request.method == 'POST':
#         form = CategoryForm(request.POST)

#         # Have we been provided with a valid form?
#         if form.is_valid():
#             # Save the new category to the database.
#             form.save(commit=True)
#             # Now that the category is saved, we could confirm this.
#             # For now, just redirect the user back to the index view.
#             return redirect(reverse('rango:index'))
#         else:
#             # The supplied form contained errors - 
#             # just orint them to the terminal.
#             print(form.errors)

#     # Will handle the bad form, new form, or no form supplied cases.
#     # Render the form with error messages (if any).
#     return render(request, 'rango/add_category.html', {'form': form})

class AddCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = CategoryForm()
        return render(request, 'rango/add_category.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)

        return render(request, 'rango/add_category.html', {'form': form})

# @login_required
# def add_page(request, category_name_slug):
#     try:
#         category = Category.objects.get(slug=category_name_slug)
#     except Category.DoesNotExist:
#         category = None

#     # You cannot add a page to a Category that does not exist...
#     if category is None:
#         return redirect('rango:index')

#     form = PageForm()

#     if request.method == 'POST':
#         form = PageForm(request.POST)

#         if form.is_valid():
#             if category:
#                 page = form.save(commit=False)
#                 page.category = category
#                 page.views = 0
#                 page.save()

#                 return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
#         else:
#             print(form.errors)

#     context_dict = {'form': form, 'category': category}
#     return render(request, 'rango/add_page.html', context=context_dict)

class AddPageView(View):
    def get_category_name(self, category_name_slug):
        """
        A helper method that was created to demonstrate the power of class-based views.
        You can reuse this method in the get() and post() methods!
        """
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None
        
        return category
    
    @method_decorator(login_required)
    def get(self, request, category_name_slug):
        form = PageForm()
        category = self.get_category_name(category_name_slug)

        if category is None:
            return redirect(reverse('rango:index'))
        
        context_dict = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context_dict)
    
    @method_decorator(login_required)
    def post(self, request, category_name_slug):
        form = PageForm(request.POST)
        category = self.get_category_name(category_name_slug)

        if category is None:
            return redirect(reverse('rango:index'))
        
        if form.is_valid():
            page = form.save(commit=False)
            page.category = category
            page.views = 0
            page.save()

            return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)
        
        context_dict = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context=context_dict)

# def register(request):
#     # A boolean value for telling the template whether the registration was successful.
#     # Set to False initially. Code changes value to True when registration succeeds.
#     registered = False

#     # If it's a HTTP POST, we're interested in processing form data.
#     if request.method == 'POST':
#         # Attempt to grab information from the raw form information.
#         # Note that we make use of both UserForm and UserProfileForm.
#         user_form = UserForm(request.POST)
#         profile_form = UserProfileForm(request.POST)

#         # If the two forms are valid...
#         if user_form.is_valid() and profile_form.is_valid():
#             # Save the user's form data to the database.
#             user = user_form.save()

#             # Now we hash the password with the set_password method. Once hashed, we can update the user object.
#             user.set_password(user.password)
#             user.save()

#             # Now sort out the UserProfile instance. 
#             # Since we need to set the user atribute ourselves, we set commit=False.
#             # This delays saving the model until we're ready to avoid integrity problems.
#             profile = profile_form.save(commit=False)
#             profile.user = user

#             # Did the user provide a profile picture? If so. we need to get it from the input form and put it in the UserProfil model
#             if 'picture' in request.FILES:
#                 profile.picture = request.FILES['picture']

#             # Now we save the UserProfile model instance
#             profile.save()

#             # Update out variable to indicate that the template registration was successful.
#             registered = True
#         else:
#             # Invalid form or forms - miostakes or something else? Print problems to the terminal.
#             print(user_form.errors, profile_form.errors)

#     else:
#         # Not a HTTP POST, so we render our form using two ModelForm instances. These forms will be blank, readu for user input.
#         user_form = UserForm()
#         profile_form = UserProfileForm()

#     # Render the template depending on the context.
#     return render(request, 'rango/register.html', context = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

# def user_login(request):
#     # If the request is a HTTP POST, try to pull out the relevant information.
#     if request.method == 'POST':
#         # Gather the username and password provided by the user.
#         # This information is obtained from the login form.
#         # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'], because the
#         # request.POST.get('<variable>') returns None if the value does not exist, 
#         # while request.POST['<variable>'] will raise a KeyError exception.
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         # User Django's machinery to attempt to see if the username/password combination is valid - a User object is returned if it is.
#         user = authenticate(username=username, password=password)

#         # If we have a User object, the details are correct.
#         # If None (Python's way of represneting the absence of a value), no user with matching credentials was found.
#         if user:
#             # Is the account active? It could have been disabled.
#             if user.is_active:
#                 # Is the account is valid and active, we can log the user in.
#                 # We'll send the user back to the homepage.
#                 login(request, user)
#                 return redirect(reverse('rango:index'))
#             else:
#                 # An inactive account was used - no logging in!
#                 return HttpResponse("Your Rango account is disabled.")
#         else:
#             # Bad login details were provided. So we can't log the user in.
#             print(f"Invalid login details: {username}, {password}")
#             return HttpResponse("Invalid login details supplied.")

#     # The request is not a HTTP POST, so display the login form.
#     # This scenario would most likely a a HTTP GET.
#     else:
#         # No context variables to pass to the template system, hence the blank dictionary object...
#         return render(request, 'rango/login.html')

# @login_required
# def restricted(request):
#      return render(request, 'rango/restricted.html')

class RestrictedView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'rango/restricted.html')

# # Use the login_required() decorator to ensure only those logged in can access the view.
# @login_required
# def user_logout(request):
#     # Since we know the user is logged in, we can now just log them out.
#     logout(request)
#     # Take the user back to the homepage.
#     return redirect(reverse('rango:index'))

# # A helper method
# def get_server_side_cookie(request, cookie, default_val=None):
#     val = request.session.get(cookie)
#     if not val:
#         val = default_val
#     return val

# def visitor_cookie_handler(request):
#     # Get the number of visits to the site. We use the COOKIES.get() fucntion to obtain the visits cookie.
#     # If the cookie exists, the value returned is caster to an integer. 
#     # If the cookie doesn't exist, then the default value of 1 is used.
#     visits = int(get_server_side_cookie(request, 'visits', '1'))

#     last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
#     last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

#     # If it's been more than a day since the last visit...
#     if (datetime.now() - last_visit_time).days > 0:
#         visits = visits + 1
#         # Update the last visit cookie now that we have updated the count 
#         request.session['last_visit'] = str(datetime.now())
#     else:
#         # Set the last visit cookie
#         request.session['last_visit'] = last_visit_cookie

#     # Update/set the visists cookie
#     request.session['visits'] = visits

# def search(request):
#     result_list = []
#     query = ''

#     if request.method == 'POST':
#         query = request.POST['query'].strip()

#         if query:
#             result_list = run_query(query)
    
#     return render(request, 'rango/search.html', {'result_list': result_list, 'query': query})

# def goto_url():
#     if request.method == 'GET':
#         page_id = request.GET.get('page_id')
#         try:
#             selected_page = Page.objects.get(id=page_id)
#         except Page.DoesNotExist:
#             return redirect(reverse('rango:index'))

#         selected_page.views = selected_page.views + 1
#         selected_page.save()
#         return redirect(selected_page.url)

#     return redirect(reverse('rango:index'))

class GotoView(View):
    def get(self, request):
        page_id = request.GET.get('page_id')

        try:
            selected_page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return redirect(reverse('rango:index'))

        selected_page.views = selected_page.views + 1
        selected_page.save()

        return redirect(selected_page.url)


# @login_required
# def register_profile(request):
#     form = UserProfileForm()

#     if request.method == 'POST':
#         form = UserProfileForm(request.POST, request.FILES)

#         if form.is_valid():
#             user_profile = form.save(commit=False)
#             user_profile.user = request.user
#             user_profile.save()

#             return redirect(reverse('rango:index'))
#         else:
#             print(form.errors)

#     context_dict = {'form': form}
#     return render(request, 'rango/profile_registration.html', context_dict)

class RegisterProfileView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = UserProfileForm()
        context_dict = {'form': form}
        return render(request, 'rango/profile_registration.html', context_dict)
    
    @method_decorator(login_required)
    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
        
        context_dict = {'form': form}
        return render(request, 'rango/profile_registration.html', context_dict)

class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        user_profile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({'website': user_profile.website,
                                'picture': user_profile.picture})
        
        return (user, user_profile, form)
    
    @method_decorator(login_required)
    def get(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))
        
        context_dict = {'user_profile': user_profile,
                        'selected_user': user,
                        'form': form}
        
        return render(request, 'rango/profile.html', context_dict)
    
    @method_decorator(login_required)
    def post(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))
        
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('rango:profile',
                                    kwargs={'username': username}))
        else:
            print(form.errors)
        
        context_dict = {'user_profile': user_profile,
                        'selected_user': user,
                        'form': form}
        
        return render(request, 'rango/profile.html', context_dict)

class ListProfilesView(View):
    @method_decorator(login_required)
    def get(self, request):
        profiles = UserProfile.objects.all()

        return render(request, 'rango/list_profiles.html', {'user_profile_list': profiles})

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    
    request.session['visits'] = visits

class LikeCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        category_id = request.GET['category_id']

        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse(-1)
        except ValueError:
            return HttpResponse(-1)
        
        category.likes = category.likes + 1
        category.save()

        return HttpResponse(category.likes)
        
def get_category_list(max_results=0, starts_with=''):
    category_list = []

    if starts_with:
        category_list = Category.objects.filter(name__istartswith=starts_with)

    if max_results > 0:
        if len(category_list) > max_results:
            category_list = category_list[:max_results]

    return category_list

class CategorySuggestionView(View):
    def get(self, request):
        if 'suggestion' in request.GET:
            suggestion = request.GET['suggestion']
        else:
            suggestion = ''
        
        category_list = get_category_list(max_results=8, starts_with=suggestion)

        if len(category_list) == 0:
            category_list = Category.objects.order_by('-likes')
        
        return render(request, 'rango/categories.html', {'categories': category_list})


class SearchAddPageView(View):
    @method_decorator(login_required)
    def get(self, request):
        category_id = request.GET['category_id']
        title = request.GET['title']
        url = request.GET['url']

        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse('Error - category not found.')
        except ValueError:
            return HttpResponse('Error - bad category ID.')
        
        p = Page.objects.get_or_create(category=category, title=title, url=url)

        pages = Page.objects.filter(category=category).order_by('-views')
        return render(request, 'rango/page_listing.html', {'pages': pages})