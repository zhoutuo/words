import os
from pyramid.response import Response, FileResponse
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
)


@view_config(route_name='home')
def home_view(request):
    directory = os.path.dirname(__file__)
    location = os.path.join(directory, 'static', 'index.html')
    return FileResponse(location)