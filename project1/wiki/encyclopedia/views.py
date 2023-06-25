from django.shortcuts import render, redirect
from random import choice
from markdown2 import markdown

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "pageTitle": "All Pages"
    })

# get an entry by clicking over his link
def getEntry(request, title):
    # check if the entry in the list
    if util.get_entry(title) is None:
        return render(request, "encyclopedia/error.html", {
            "errorMassage": "This Entry Not Exist!!"
        })
    else:
        # Markdown to HTML Conversion, render 
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown(util.get_entry(title)),
            "title": title
        })

# search for an entry
def searchEntry(request):
    # get form data
    query = request.GET.get('q')
    # check if the user submit an empyt form
    if not query:
        return render(request, "encyclopedia/error.html",{
            "errorMassage": "You have to type something in the search bar"
        })
    else:
        # if there is no matching with an existing entry
        if util.get_entry(query) is None:
            entries = util.list_entries()
            # look for substring
            matchingEntries = [entry for entry in entries if query.lower() in entry.lower()]
            if matchingEntries:
                return render(request, "encyclopedia/index.html", {
                    "pageTitle": "Those are matching entries",
                    "entries": matchingEntries
                })
            # if there is not even a substring of that query
            else:
                return render(request, "encyclopedia/error.html", {
                "errorMassage": "This Entry Not Exist!!"
                })
        # if there is a matching entry
        else:
            return render(request, "encyclopedia/entry.html", {
                "entry": markdown(util.get_entry(query)),
                "title": query
            })
        
# creat a new entry
def create(request):
    if request.method == "GET":
        return render (request, "encyclopedia/create.html")
    else:
        # get form data
        title = request.POST.get('title')
        content = request.POST.get('content')
        # Check if the title not match with an existing title
        if util.get_entry(title) is None:
            # save the entry
            util.save_entry(title, content)
            # redirect to the entry page
            return render(request, "encyclopedia/entry.html", {
            "entry": markdown(util.get_entry(title)),
            "title": title
            })
        # if the title already exist
        else:
            return render(request, "encyclopedia/create.html", {
                "errorMassage": "Sorry, The title you provided is already exist, coude you change the title.",
            })
        
# edit Entry
def editEntry(request, title):
    if request.method == "GET":
        # display the form with the content
        return render(request, "encyclopedia/edit.html", {
                "old_content": util.get_entry(title),
                "title": title
            })
    else:      
        # check if the user change the title some way (if that happen django redirect the user to "wiki/title/edit")
        
        # get the new content from the form
        newContent = request.POST.get('content')
        # save the entry
        util.save_entry(title, newContent)
        # redirect to the entry page
        return render(request, "encyclopedia/entry.html", {
        "entry": markdown(util.get_entry(title)),
        "title": title
        })

# random entry
def randomEntry(request):
    # get a random entry
    random = choice(util.list_entries())
    return render (request, "encyclopedia/entry.html", {
        "entry": markdown(util.get_entry(random)),
        "title": random
    })