from __future__ import unicode_literals
import os
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ModelForm


class RdfUpload(models.Model):

    title = models.CharField(max_length=64)
    owner = models.CharField(max_length=64, default='Name' )
    rdf_file = models.FileField("File", upload_to="rdfs/")
    upload_date = models.DateTimeField(auto_now_add=True)
    project_ID = models.CharField(max_length=128, default=None)
    corpus_ID = models.CharField(max_length=128, default=None)

    def __unicode__(self):
        return str(self.upload_date)


def changed_filename_path(instance, filename):
    return os.path.join("thesaurus_data/", instance.project_ID + ".rj")


class ThesaurusUpload(models.Model):

    title = models.CharField(max_length=64)
    thesaurus_file = models.FileField("File", upload_to=changed_filename_path, help_text="Please upload a file with a '.rj' extension.You can find this in the PoolParty-exporting options of the project.")
    upload_date = models.DateTimeField(auto_now_add=True)
    project_ID = models.CharField(max_length=128, default=None)

    def __unicode__(self):
        return str(self.upload_date)


# FileUpload form class.
class UploadForm(ModelForm):

    def clean_rdf_file(self):
        file = self.cleaned_data['rdf_file']
        filename = str(file)
        if not "rdf" in filename:
            raise ValidationError("File is not RDF")
        return file

    def clean_project_ID(self):
        return self.cleaned_data['project_ID']

    def clean_corpus_ID(self):
        return self.cleaned_data['corpus_ID']

    class Meta:
        model = RdfUpload
        fields = ['title', 'owner', 'project_ID', 'corpus_ID', 'rdf_file',]


class UploadForm2(ModelForm):

    class Meta:
        model = ThesaurusUpload
        fields = ['title', 'project_ID', 'thesaurus_file']

    def clean_thesaurus_file(self):
        file = self.cleaned_data['thesaurus_file']
        filename = str(file)
        if not "rj" in filename:
            raise ValidationError("Please upload a file with an '.rj' extension.")
        return file

    def clean_project_ID(self):
        return self.cleaned_data['project_ID']

    def clean_title(self):
        return self.cleaned_data['title']

    def clean_thesaurus_filename(self):
        filename = self.cleaned_data['thesaurus_file']
        return str(filename)




