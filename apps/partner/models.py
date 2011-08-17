import os
import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _

from autoslug.fields import AutoSlugField
from imagekit.models import ImageModel

from apps.project_sheet.models import I4pProject

class Partner(models.Model):
    """
    A partner is a supporting organisation that is linked to a number
    of project sheets
    """
    slug = AutoSlugField(populate_from='name',
                         always_update=True)

    name = models.CharField(verbose_name=_('name'),
                            max_length=255)

    description = models.TextField(verbose_name=_('description'),
                                   null=True, blank=True)
    
    website = models.URLField(verbose_name=_('website'))

    projects = models.ManyToManyField(I4pProject,
                                      verbose_name=_("supported projects"),
                                      blank=True)
                                      
    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('partner-detail', (self.slug,))

def get_partnerpicture_path(aPartnerPicture, filename):
    """
    Generate a random UUID for a picture,
    use the uuid as the picture name
    """
    picture_uuid = uuid.uuid4()
    name, extension = os.path.splitext(filename)

    dst = 'uploads/partners/%d/pictures/%s%s' % (aPartnerPicture.partner.id,
                                                 picture_uuid,
                                                 extension)
    return dst


class PartnerPicture(ImageModel):
    """
    A picture of a partner (logo for e.g.)
    """
    class IKOptions:
        spec_module = 'apps.partner.picture_specs'
        image_field = 'original_image'
    
    original_image = models.ImageField(upload_to=get_partnerpicture_path)
    partner = models.OneToOneField(Partner, related_name='picture')
    

