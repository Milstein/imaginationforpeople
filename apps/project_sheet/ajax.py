import urllib

from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404
from django.utils import simplejson, translation

from dajax.core import Dajax
from dajaxice.core import dajaxice_functions

from tagging.models import Tag
from tagging.utils import get_tag_list, parse_tag_input

from .models import I4pProject, I4pProjectTranslation
from .forms import I4pProjectObjectiveForm, I4pProjectThemesForm
from .utils import get_or_create_project, get_or_create_project_translation_by_slug, get_project_translation_by_slug

from django.http import QueryDict, HttpResponse, HttpResponseNotFound
from django.utils import simplejson

from django.views.decorators.csrf import csrf_exempt
from django.template.defaultfilters import linebreaksbr

TEXTFIELD_MAPPINGS = {
    'about_section_txt': 'about_section',
    'project_uniqueness_txt': 'uniqueness_section',
    'project_value_txt': 'value_section',
    'project_scalability_txt': 'scalability_section'
    }

def project_textfield_load(request, project_slug=None):
    """
    Load the source of a text field (project description, ...),
    without the markup rendered (useful for JS editing, to prevent
    html tags from being edited without interpretation).
    """
    if not project_slug:
        return HttpResponse('')

    language_code = request.GET['language_code']
    section = request.GET['id']

    # Check if we allow this field
    if not section in TEXTFIELD_MAPPINGS:
        return HttpResponseNotFound()

    # Activate requested language
    translation.activate(language_code)

    # get the project translation and its base
    project_translation = get_project_translation_by_slug(project_translation_slug=project_slug,
                                                          language_code=language_code)

    # Get the text
    text = getattr(project_translation, TEXTFIELD_MAPPINGS[section])

    return HttpResponse(text or '')

@csrf_exempt
def project_textfield_save(request, project_slug=None):
    """
    Edit a text field
    """
    language_code = request.POST['language_code']
    section = request.POST['id']
    value = request.POST['value']

    # Activate requested language
    translation.activate(language_code)

    project_translation = get_or_create_project_translation_by_slug(project_translation_slug=project_slug, 
                                                                    language_code=language_code)
    
    # Check if we allow this field
    if not section in TEXTFIELD_MAPPINGS:
        return HttpResponseNotFound()

    # Resolve the fieldname
    fieldname = TEXTFIELD_MAPPINGS[section]

    FieldForm = modelform_factory(I4pProjectTranslation, fields=(fieldname,))

    form = FieldForm({fieldname: value}, instance=project_translation)

    if form.is_valid():
        form.save()
        return HttpResponse(simplejson.dumps({'text': linebreaksbr(value),
                                              'redirect': project_slug is None,
                                              'redirect_url': project_translation.get_absolute_url()}), 'application/json')
    else:
        return HttpResponseNotFound()


def project_update_related(request, language_code, related_form, project_slug):
    """
    Update themes and objective of a given project, in a given language
    """
    # Activate requested language
    translation.activate(language_code)

    # get the project translation and its base
    project_translation = get_project_translation_by_slug(project_translation_slug=project_slug,
                                                          language_code=language_code)

    parent_project = project_translation.project

    project_objective_form = I4pProjectObjectiveForm(related_form,
                                                     instance=parent_project)


    # Convert tags to string list, separated by comma
    if isinstance(related_form['themes'], list):
        related_form['themes'] = ", ".join(related_form['themes'])

    project_themes_form = I4pProjectThemesForm(related_form,
                                               instance=project_translation)


    if project_themes_form.is_valid() and project_objective_form.is_valid():
        # Use Tag otherwise it doesn't work because of the proxy model
        project_themes_form.save()
        #Tag.objects.update_tags(project_sheet.get_translation(), related_form['themes'])

        # Save objective
        project_objective_form.save()

    return simplejson.dumps({})



#dajaxice_functions.register(project_sheet_edit_field)
dajaxice_functions.register(project_update_related)





