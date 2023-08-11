from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User,Category, AuctionListing, Bid, Comment, Watchlist, Notification
from .forms import ListingForm, BidForm

# django flash messages
from django.contrib import messages


def index(request):
    # get the categorie
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    listings = AuctionListing.objects.filter(
        Q(is_active=True) &
        Q(category__name__icontains=q)
        )
    Categories = Category.objects.all()
    context = {'listings':listings,
               'Categories':Categories}
    return render(request, "auctions/index.html", context)

def Profile(request):
    listings = AuctionListing.objects.filter(owner=request.user)

    context = {"listings":listings}
    return render(request, "auctions/profile.html", context)
    


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

    # is the listing added to the watchlist
    is_in_watchlist = False
    if request.user.is_authenticated:
        is_in_watchlist = Watchlist.objects.filter(user=request.user, listing=listing_page).exists()

    # if user make a bid 
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
               'last_bid':last_bid, 'comments':comments,
               'Bidders':Bidders, 'is_in_watchlist':is_in_watchlist}
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
def watchlistPage(request):
    # get the objects associated with the watchlist of the user
    watched_listings = Watchlist.objects.filter(user=request.user).values('listing')
    # get the primary key of the listings in the watched_listings queryset
    listing_pks = watched_listings.values_list('listing', flat=True)
    # get the listings from there primary keys
    watched_listings_data = AuctionListing.objects.filter(pk__in=listing_pks)

    print(f"watched_listings: |{watched_listings}|listing_pks: |{listing_pks}| DATA: |{watched_listings_data}|")
    context = {'watched_listings': watched_listings_data}
    return render(request, 'auctions/watchlist.html', context)


def addWatchlist(request, pk):
    listing_page = AuctionListing.objects.get(id=pk)
    if request.method == "POST": 
        Watchlist.objects.create(user=request.user, listing=listing_page)
        return redirect("listingPage", pk=listing_page.id)

def removeWatchlist(request, pk):
    listing_page = AuctionListing.objects.get(id=pk)
    if request.method == "POST":
        Watchlist.objects.filter(user=request.user, listing=listing_page).delete()
        return redirect("listingPage", pk=listing_page.id)
    
# Auction Control
def AuctionControl(request, pk):
    listing_page = AuctionListing.objects.get(id=pk)
    if request.method == "POST":
        if listing_page.is_active: #if it's active --> close it
            # check if there are any bidders
            last_bid = Bid.objects.filter(listing=listing_page).first()
            print(last_bid.bidder)
            if last_bid: # there is a bidder --> process winner notification and ownership transfer
                listing_page.is_active = False
                listing_page.owner = last_bid.bidder 
                listing_page.save()
                # CREATE A NOTIFICATION sented to the winner
                
                notification = Notification.objects.create(user=last_bid.bidder, listing=listing_page)
                messages.success(request, f"You have been successfully Closed this auction, the new owner of this auction is @{last_bid.bidder}")
            else: # no bidders --> just close the auction
                listing_page.is_active = False
                listing_page.save()
                messages.success(request, "You have been successfully Closed this auction.")

            return redirect("listingPage", pk=listing_page.id)
        else: #if it's not active --> activate it
            listing_page.is_active = True
            listing_page.save()
            messages.success(request, "You have been successfully Activate this auction.")
            return redirect("listingPage", pk=listing_page.id)
        
        
def Notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    
    notifications.update(is_read=True)
    context = {"notifications":notifications}
    return render(request, 'auctions/Notifications.html', context)
        
    