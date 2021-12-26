from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from src.ohara import Ohara
# Create your views here.

def upload(request):
    return render(request, 'ohara/upload.html', {})

def text_handler(request):
    bibDir = './ohara/bib/'
    ohara = Ohara(bibDir)
    bibtex = request.POST['bibtex']
    lines = bibtex.split('\n')
    firstline = lines[0]
    fname = firstline[firstline.find("/")+1:firstline.find(",")]
    fpath = bibDir+fname+'.bib'
    with open(fpath, 'w', encoding = 'utf-8') as f:
        f.write(bibtex)
    ohara.add_entry_from_file(fpath)
    return HttpResponseRedirect(reverse('ohara:success'))

def success(request):
    return render(request, 'ohara/success.html', {})

def return_to_upload(request):
    return HttpResponseRedirect(reverse('ohara:upload'))

def view_in_notion(request):
    ohara = Ohara('.')
    return HttpResponseRedirect(ohara.get_notion_page_url())