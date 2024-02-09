from django import forms


class CommentForm(forms.Form):
    content = forms.CharField(label='Comment', widget=forms.Textarea(attrs={'rows': 3}))


class ConversationForm(forms.Form):
    recipient = forms.CharField(label='Recipient', max_length=100)
    message = forms.CharField(label='Message', widget=forms.Textarea)
