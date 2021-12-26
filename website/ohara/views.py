from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from src.ohara import Ohara
import os
# Create your views here.

def upload(request):
    return render(request, 'ohara/upload.html', {})

def text_handler(request):
    bibDir = './ohara/bib/'
    ohara = Ohara(bibDir)
    bibtex = request.POST['bibtex']
    lines = bibtex.split('\n')
    firstline = lines[0]
    if firstline.find('/') >= 0:
        fname = firstline[firstline.find("/")+1:firstline.find(",")]+'.bib'
    else: 
        fname = firstline[firstline.find("{")+1:firstline.find(",")]+'.bib'
    fpath = bibDir+fname
    file_exist = False
    for dirName, subdirList, fileList in os.walk(ohara.rootDir):
        if fname in fileList:
            file_exist = True
            break
    if file_exist:
        print(reverse('ohara:repeat_entry_warning', args = (fname,)))
        return HttpResponseRedirect(reverse('ohara:repeat_entry_warning', args = (fname,)))
    else:
        with open(fpath, 'w', encoding = 'utf-8') as f:
            f.write(bibtex)
        ohara.add_entry_from_file(fpath)
    return HttpResponseRedirect(reverse('ohara:success'))

def repeat_entry_warning(request, fname):
    warning_msg = fname + " is already in Ohara!"
    return render(request, 'ohara/warning.html', {
            'warning_msg': warning_msg,
        })

def success(request):
    return render(request, 'ohara/success.html', {})

def return_to_upload(request):
    return HttpResponseRedirect(reverse('ohara:upload'))

def view_in_notion(request):
    ohara = Ohara('.')
    return HttpResponseRedirect(ohara.get_notion_page_url())