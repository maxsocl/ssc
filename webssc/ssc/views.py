from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
import socket
import ConfigParser
import os


PATH = os.path.realpath(os.path.dirname(__file__))

city = ['KHARKOV', 'ODESSA', 'DONETSK', 'KIEV', 'DNEPR', 'POLTAVA', 'MARIUPOL']
point = ['K0', 'K2', 'K01', 'K02', 'K03', 'K04', 'K05', 'K06', 'K08', 'K11',
         'K12', 'K13', 'K14', 'K45', 'K20', 'X00']


config = ConfigParser.RawConfigParser()
config.read(PATH + '/../ssc_conf.ini')
host = config.get('server', 'server_ip')
port = int(config.get('server', 'server_port'))


def user_login(request):
    """
    Login func
    """
    if request.user.is_authenticated():
        return TemplateResponse(request, 'ssc/already_logged.html')
    else:
        return views.login(request, template_name='ssc/login.html')


def user_logout(request):
    """
    Logout func
    """
    if request.user.is_authenticated():
        return views.logout(request, next_page=reverse('ssc:goodbye'))
    else:
        return TemplateResponse(request, 'ssc/not_logged.html')


def client_request(user, login_name, method):
    """
    Make connection to server
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((host, port))
    except Exception as e:
        return str(e)

    else:
        s.send(user)
        response = s.recv(64)

        if response == 'ok':
            s.send(login_name)
            response = s.recv(24)
            if response == 'ok':
                s.send(method)
                response = s.recv(2048)
    finally:
        s.close()
        return response


def ssc(request):
    """Common code for making similar logic for http_request and ajax_request.

    DRY similar code between simple HTTP and Ajax requests to this function.
    Using client_request function for making request to socket server.
    Returning response as a dictionary.
    """

    delete = False
    result = False
    login_name = False
    user = request.user.username
    # Deleting session(second) part of request
    if (request.method == 'POST' and 'login_del' in request.POST and
                                    request.POST['submit'] == 'Delete'):

        login_name = request.POST['login_del']

        result = client_request(user, login_name, method='del')
        result = result.split('\n')
        return {'result': result, 'login_name': login_name, 'delete': delete}

    # Listening session(first) part of request - mandatory part
    elif request.method == 'POST' and 'login_name' in request.POST:
        # If user choise first option - write SSID in text mode
        if request.POST['type'] == 'raw' and request.POST['login_name'] != '':
            login_name = request.POST['login_name']
        # If user choise second option - to compound SSID
        elif request.POST['type'] == 'comp':
            try:
                opt1 = str(int(request.POST['opt1']))
                opt2 = str(int(request.POST['opt2']))
                if len(str(int(request.POST['opt3']))) == 1:
                    opt3 = '0' + str(int(request.POST['opt3']))
                else:
                    opt3 = str(int(request.POST['opt3']))
                opt4 = '0' + str(int(request.POST['opt4']))
                opt5 = str(int(request.POST['opt5']))
                opt6 = str(int(request.POST['opt6']))
                opt7 = str(int(request.POST['opt7']))
            except ValueError:
                result = ['Incorrect input.']
                return {'result': result, 'login_name': login_name, 'delete': delete}

            login_name = (request.POST['city'] + '-' + request.POST['point'] +
                          ' PON ' + opt1 + '/' + opt2 + '/' + opt3 + '/' +
                          opt4 + ':' + opt5 + '.' + opt6 + '.' + opt7)
        else:
            result = ['Incorrect input.']
            return {'result': result, 'login_name': login_name, 'delete': delete}

        result = client_request(user, login_name, method='list')

        if ('No sessions' in result or 'Syntax' in result or
            result == 'Connection lost.' or 'not allowed' in result):
            # Negative respone
            result = result.split('\n')
            return {'result': result, 'login_name': login_name, 'delete': delete}

        else:
            # Positive response
            msg_result = {}
            sec = 1

            # Separating different sessions
            for base_part in result.split('SessionParcel'):
                if len(base_part) == 0:
                    continue
                msg_result['Session ' + str(sec)] = []
                # Separating session parameters
                for i in base_part.split('\n'):
                    if '=' in i and \
                       ('Timestamp' in i or 'UserIpAddr' in i
                        or 'Domain' in i or 'NASPort' in i):

                        msg_result['Session ' + str(sec)].append(i)
                sec += 1

            delete = True
            result = msg_result
            return {'result': result, 'login_name': login_name, 'delete': delete}

    # GET method received - showing clear form
    else:
        return {'result': result, 'login_name': login_name, 'delete': delete}


@login_required(login_url='/ssc/accounts/login/')
def http_request(request):
    """Simple HTTP request

    render template with respone as a dictionary
    """
    response = ssc(request)
    # Adding choises for select input in from.html
    #######################################
    response['city'] = city
    response['point'] = point
    #######################################
    return TemplateResponse(request, 'ssc/form.html', response)


@login_required(login_url='/ssc/accounts/login/')
def ajax_request(request):
    """Ajax HTTP request handler

    return HTTP response as list
    """
    return HttpResponse(ssc(request)['result'])


@login_required(login_url='/ssc/accounts/login/')
def xml(request):
    """Making request to SSC API.

    Construct HTTP  request to SSC including appropriate XML data included.
    Returning response as a dictionary.
    """