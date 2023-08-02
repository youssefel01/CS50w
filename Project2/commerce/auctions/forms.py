from django import forms
from .models import AuctionListing, Bid

# adding forms

class ListingForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = ["title", "description", "primary_price", "imageUrl", "is_active", "category"]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'primary_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'imageUrl': forms.URLInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["amount"]
        labels = {
            'amount': 'Enter your bid amount',
        }

        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'})
        }
