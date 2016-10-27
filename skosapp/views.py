import json
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse, resolve
from django.contrib.auth import views, tokens, decorators
from django.views.generic import DetailView
import requests
from .models import RdfUpload, UploadForm, UploadForm2
from common.util.skos_tool import SkosTool
from common.util import corpus_util
import os.path
import pickle

def changed_filename_path(instance, filename):
    return os.path.join("thesaurus_data/", "trolol.js")

def index(request):
    return render(request, 'skosapp/home.html')


def contact(request):
    return render(request, 'skosapp/basic.html', {'data': ['Email', 'fameri@txstate.edu']})


def about(request):
    return render(request, 'skosapp/basic.html', {'data': ['todo', 'todo']})


def upload(request):
    """
    If POST, this view will validate and attempt to save the RDFUpload instance to the
    database. If GET, serve the Upload form
    :param request: request
    :return: if POST, send RDF to the tool for parsing and display results, otherwise, return
                a rendering of the UploadForm
    """

    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            # save to session for ease of use between views
            request.session['rdf'] = instance.id
            project = form.clean_project_ID()
            corpus = form.clean_corpus_ID()

            corpus_util.get_corpus_data(corpus_file='corpus_data/' + corpus + '.json', corpus_id = corpus, project_id=project)

            request.session['location'] = 'corpus_data/' + corpus + '.json'
            return HttpResponseRedirect(reverse('skos'))
    else:
        form = UploadForm()

    return render(request, 'skosapp/upload.html', {'form': form})


def skos(request):
    """
    View that contains
    :param request:
    :return:
    """

    pk = request.session.get('rdf', default=None)

    location = request.session['location']

    if pk:
        rdf = RdfUpload.objects.get(pk=pk)
        skos_tool = SkosTool(rdf_path=rdf.rdf_file.path)
        skos_tool.parse()
        skos_tool.get_frequencies(filename=location)
        skos_tool.sort()
        results = skos_tool.get_metrics()


        return render(request, 'skosapp/results.html', {'results': results})
    else:
        #TODO template that displays the user that something went wrong
        #TODO with the processing of the rdf file
        return render(request, 'skosapp/oops.html')


def corpus(request):
    """
    view for kicking off a PoolParty sync
    :param request:
    :return:
    """
    return render(request, 'skosapp/corpus.html')


def corpus_fetch(request):
    """
    executes PoolParty sync and then redirects to the upload view
    :param request:
    :return:
    """
    #corpus_util.get_corpus_data()
    return HttpResponseRedirect(reverse('upload'))

def uploadText(request):

    if(os.path.exists('media/thesaurus_data/thesaurus_dict.pickle')):

            with open('media/thesaurus_data/thesaurus_dict.pickle', 'rb') as handle:
                    thesaurus_dict = pickle.load(handle)
    else:
        thesaurus_dict = {}

    if request.method == 'POST':
        selected_thesaurus = request.POST.get("select_thesaurus")
        id = thesaurus_dict[selected_thesaurus]

        with open('media/thesaurus_data/' + id + '.rj') as json_data:
            d = json.load(json_data)
            thesaurus = []
            myDict = {}

            label = ""
            count = 0
            for key, value in d.iteritems():

                if 'http://www.w3.org/2004/02/skos/core#prefLabel' in value:
                    label = value['http://www.w3.org/2004/02/skos/core#prefLabel'][0]['value']
                    count += 1
                    thesaurus.append(label)

                if 'http://www.w3.org/2000/01/rdf-schema#label' in value:
                    count += 1
                    if(label != value["http://www.w3.org/2000/01/rdf-schema#label"][0]['value']):
                        thesaurus.append(value["http://www.w3.org/2000/01/rdf-schema#label"][0]['value'])

                if 'http://www.w3.org/2004/02/skos/core#altLabel' in value:
                    count += 1
                    for label in value['http://www.w3.org/2004/02/skos/core#altLabel']:
                        thesaurus.append(label['value'])

                if 'http://www.w3.org/2004/02/skos/core#hiddenLabel' in value:
                    count += 1
                    for label in value['http://www.w3.org/2004/02/skos/core#hiddenLabel']:
                        thesaurus.append(label['value'])

        text = request.POST.get('text_area')
        print(text)
        json_thesaurus = json.dumps(thesaurus)


        return render(request, 'skosapp/analyze_results.html', {'json_thesaurus': json_thesaurus,
                                                                'text':text})
    else:

        return render(request, 'skosapp/tagging.html', {'thesaurus_dict':thesaurus_dict})

def uploadThesaurus(request):

    if request.method == "POST":
        form = UploadForm2(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            project_id = form.clean_project_ID()
            title = form.clean_title()

            if os.path.exists('media/thesaurus_data/thesaurus_dict.pickle'):
                with open('media/thesaurus_data/thesaurus_dict.pickle', 'rb') as handle:
                    thesaurus_dict = pickle.load(handle)

                    if project_id not in thesaurus_dict.values():
                        thesaurus_dict[title] = project_id
                        instance.save()
                        with open('media/thesaurus_data/thesaurus_dict.pickle', 'wb',) as handle:
                            pickle.dump(thesaurus_dict, handle)

            else:
                instance.save()
                thesaurus_dict = {}
                thesaurus_dict[title] = project_id
                with open('media/thesaurus_data/thesaurus_dict.pickle', 'wb',) as handle:
                    pickle.dump(thesaurus_dict, handle)

            return HttpResponseRedirect(reverse('tagging'))

    else:
        form = UploadForm2()

    return render(request, 'skosapp/upload_thesaurus.html', {'form':form})
