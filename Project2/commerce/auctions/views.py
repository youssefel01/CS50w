from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, AuctionListing, Bid, Comment
from .forms import ListingForm, BidForm

# django flash messages
from django.contrib import messages


def index(request):
    active_listings = AuctionListing.objects.filter(is_active=True)
    context = {'active_listings':active_listings}
    return render(request, "auctions/index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
# a function for adding listing
def CreateListing(request):
    form = ListingForm()

    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.creater = request.user
            listing.save()
            return redirect('index')

    context = {'form':form}
    return render(request, 'auctions/Listing_form.html', context)
    


# a function for geting the listing page
def listingPage(request, pk):
    listing_page = AuctionListing.objects.get(id=pk)
    comments = Comment.objects.filter(listing=listing_page)
    # get the last bid for this listing, if any
    last_bid = Bid.objects.filter(listing=listing_page).first()
    # get the Bidders in this lisitng
    Bidders = Bid.objects.filter(listing=listing_page)
    # if user bid aka post
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid_amount = form.cleaned_data['amount']

            if not last_bid and bid_amount <= listing_page.primary_price:
                    print("with primary price")
                    messages.warning(request, "Your Bid Is Unsuitable")
            elif last_bid and bid_amount <= last_bid.amount:
                print("with last bid")
                messages.warning(request, "Your Bid Is Unsuitable")
            else:
                print("in the way to be saved")
                bid = form.save(commit=False)
                bid.bidder = request.user 
                bid.listing = listing_page
                bid.save()
                print("it's SAVE")
                # Empty form after successful bid
                form = BidForm()  # Instantiate a new form to clear the input field
                return redirect("listingPage", pk=listing_page.id)
    else:
        form = BidForm()

    context = {'listing_page':listing_page,'form':form,
               'last_bid':last_bid, 'comments':comments, 'Bidders':Bidders}
    return render(request, 'auctions/listing_page.html', context)

# user add a comment
def listingComment(request, pk):
    listing_page = AuctionListing.objects.get(id=pk)
    if request.method == "POST":
        comment = Comment.objects.create(
            creater = request.user,
            listing = listing_page,
            body = request.POST.get('body')
        )
    
    return redirect("listingPage", pk=listing_page.id)

# Watchlist
def Watchlist(request, pk):

    if request.method == "POST":
        pass

    else:
        pass