''' My Application '''

import re

import yaml

from quick_scheme import KeyBasedList
from quick_scheme import ListOfReferences, ListOfNodes
from quick_scheme import SchemeNode, Field
from quick_scheme import qs_yaml


DATA = '''
version: 1
updates:
  # this is our update log to demonstrate lists 
  - '2019-08-14: initial version'
  - '2019-08-15: added user3'
  - '2019-08-15: added project2'
users:
  user1:
    first_name: User
    last_name: One
  user2:
    first_name: Another
    last_name: User
    email: another.user@mydomain.com
    desc: Another User
  user3:
    first_name: Another
    last_name: User
    email: another.user@mydomain.com
    desc: Another User

groups:
  users:
    desc: Regular Users
  admins: Admins

projects:
  project1:
    desc: My First Project
    order: 1
    users:
      - user1
    groups:
      - admins
  project2:
    desc: My Other Project
    order: 3
    groups:
      - users
'''


EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def email_validator(field_value):
    ''' Validate email '''
    email = field_value.get()
    if not email and not field_value.is_required:
        return True
    return EMAIL_REGEX.match(field_value.get())


class Group(SchemeNode):
    FIELDS = [
        Field('groupname', identity=True),
        Field('desc', brief=True),
    ]


class User(SchemeNode):
    FIELDS = [
        Field('username', identity=True),
        Field('first_name', type=str, default="", required=True),
        Field('last_name', type=str, default="", required=True),
        Field('email', type=str, default="",
              required=False, validator=email_validator),
        Field('desc', type=str, default="No Description",
              required=False, brief=True),
        Field('groups', ftype=ListOfReferences(
            Group, ".groups", False), required=False),
    ]


class Project(SchemeNode):
    FIELDS = [
        Field('name', identity=True),
        Field('desc', default="No Description"),
        Field('order', ftype=int, required=True),
        Field('users', ftype=ListOfReferences(User, ".users"), required=False),
        Field('groups', ftype=ListOfReferences(
            Group, ".groups"), required=False),
    ]


class Data(SchemeNode):
    FIELDS = [
        Field('version', ftype=str, default='1'),
        Field('updates', ftype=ListOfNodes(str)),
        Field('groups', ftype=KeyBasedList(Group)),
        Field('users', ftype=KeyBasedList(User)),
        Field('projects', ftype=KeyBasedList(Project))
    ]

    PRESERVE_ORDER = True
    ALLOW_UNDEFINED = True


def main():
    ''' Main test '''

    data = Data(data=qs_yaml.safe_load(DATA))
    print("=====\nData:\n=====\n%s=====\n" %
          qs_yaml.pretty_dump(data.quick_scheme.get_data()))


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    main()
