from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext

from ..forms.widgets import DecimalInput
from ..product.forms import registry

class QuantityForm(object):

    def clean_quantity(self):
        val = self.cleaned_data['quantity']
        if val < 0:
            raise forms.ValidationError(ugettext("Quantity cannot be negative"))
        return val


class AddToCartForm(forms.Form, QuantityForm):
    """
    Form that adds a Variant quantity to a Cart.

    It may be replaced by more advanced one, performing some checks, e.g.
    verifying the number of items in stock.
    """

    quantity = forms.DecimalField(_('Quantity'), initial=1)

    def __init__(self, data=None, *args, **kwargs):
        self.cart = kwargs.pop('cart', None)
        super(AddToCartForm, self).__init__(data=data, *args, **kwargs)

    def clean(self):
        data = super(AddToCartForm, self).clean()
        if 'quantity' in data:
            qty = data['quantity']
            add_result = self._verify_quantity(qty)
            if add_result.quantity_delta < qty:
                raise forms.ValidationError(add_result.reason)
        return data

    def _verify_quantity(self, qty):
        return self.cart.add_item(self.get_variant(), qty, dry_run=True)

    def save(self):
        return self.cart.add_item(self.get_variant(),
                                  self.cleaned_data['quantity'])

    def get_variant(self):
        raise NotImplementedError()

class EditCartItemForm(forms.ModelForm, QuantityForm):
    request_marker = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        widgets = {
            'quantity': DecimalInput(min_decimal_places=0),
        }

    def __init__(self, *args, **kwargs):
        super(EditCartItemForm, self).__init__(*args, **kwargs)
        self.is_bound = (self.is_bound and
                         self.add_prefix('request_marker') in self.data)
        if not self.is_bound:
            self.data = None

    def clean_quantity(self):
        qty = super(EditCartItemForm, self).clean_quantity()
        qty_result = self.instance.cart.replace_item(self.instance.variant, qty,
                                                     dry_run=True)
        if qty_result.new_quantity < qty:
            raise forms.ValidationError(qty_result.reason)
        return qty_result.new_quantity

    def save(self, commit=True):
        """
        Do not call the original save() method, but use cart.replace_item()
        instead.
        """
        self.instance.cart.replace_item(self.instance.variant,
                                        self.cleaned_data['quantity'])


def add_to_cart_variant_form_for_product(product,
                                         addtocart_formclass=AddToCartForm,
                                         registry=registry):
    variant_formclass = registry.get_handler(type(product))
    class AddVariantToCartForm(variant_formclass, addtocart_formclass):
        pass
    return AddVariantToCartForm
