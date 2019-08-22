[![Build Status](https://travis-ci.org/mlasevich/QuickScheme.svg?branch=master)](https://travis-ci.org/mlasevich/QuickScheme)
[![Coverage Status](https://coveralls.io/repos/github/mlasevich/QuickScheme/badge.svg?branch=master)](https://coveralls.io/github/mlasevich/QuickScheme?branch=master)
[![PyPI version](https://badge.fury.io/py/QuickScheme.svg)](https://badge.fury.io/py/QuickScheme)

# QuickScheme - Quick Way To Define Data Schema and Mapping Data To Objects

| ***⚠️WARNING*** : This is currently a _Work in Progress_ and is not ready for general use yet |
| :---: |

## QuickScheme Release Notes
* 0.2.1
    * Add field not set hooks
* 0.2.0
    * Add before/instead/after field set hooks
* 0.1.1
    * Add Validators
* 0.1.0
    * Initial version

## Quick Intro to QuickScheme

QuickScheme is a quick and easy to map arbitrary data in any python dict to an object without
forcing markup of the data file.

This allows easy data definition in YAML or JSON files including references, defaults, etc


## Features

* Easily load standard python data (from python dict, or json or yaml)
* Allow use of the data directly in Python code
* Produce "inflated" data with default values and references populated
* Do all of this without relying on custom markup in the source data

## Usage

### Basic Example Walkthrough

| NOTE: This example exists in examples directory as "basic.py" |
| :---: |

To get the most out of QuickScheme you need to define the objects your schema consists of.

for example if we want to process a yaml file like this:

      version: 1
      updates:
        # this is our update log to demonstrate lists 
        - 2019-08-14: initial version
        - 2019-08-15: added user3
        - 2019-08-15: added project2
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
            users:
              - user1
            groups:
              - admins
          project2:
            desc: My Other Project
            groups:
              - users

So, what we have here is a version of the file, a list of users and groups and list of projects. 
A few interesting things:

* **admin** group is defined by a string instead of a mapping
* Users contain references to groups by a key
* Similarly projects contain references to both users and groups

So, to be easily this we define our objects that represent the entities:

Let us define Group first:

    class Group(SchemeNode):
        FIELDS = [
            Field('groupname', identity=True),
            Field('desc', brief=True, default='No Description')
        ]

What is happening here:
* We define an object called Group which extends our SchemeNode(a field defined mapping) with two 
    fields:
    * _groupname_ - which is an identity field, meaning it is  populated from the id of the field.
      If this object is in a mapping, this would be populated from the item's key, if it is in a
      sequence, it will be populated with sequence index number
    * _desc_ - our description. We specify a default value. We also mark it as our **brief** field,
      meaning if the item is specified as a string instead of a mapping, we will populate this field

This takes care of how we defined **admin** group and allows us to know the groupname if we are
working with this object directly in python.

Next lets define User

    class User(SchemeNode):
        FIELDS = [
            Field('username', identity=True),
            Filed('userid', ftype=int, required=True),
            Field('first_name', default="", required=True),
            Field('last_name', default="", required=True),
            Field('email', default="", required=False),
            Field('desc', default="No Description", required=False),
            Field('groups', ftype=ListOfReferences(Group, ".groups", False),
                  default=[], required=False),
        ]

What is happening here:
* Similar to `Group` object we extended `SchemeNode` to create a field based mapping in which:
    * We defined identity field `username`
    * We defined an integer field `userid` - and made it a required field
    * We added two more required fields `first_name` and `last_name` - which are both strings because
      **ftype** is omitted
    * We added optional `email` and `desc` fields - with latter having a default value
    * And we added a `groups` field, wich is a list of references to Group objects which are to be
      resolved against 'groups' subkey of the root document.

Lastly We need a Project object:


    class Project(SchemeNode):
        FIELDS = [
            Field('projectname', identity=True),
            Field('order', ftype=int, required=True),
            Field('users', ftype=ListOfReferences(User, ".users"),
                  default="", required=True),
            Field('groups', ftype=ListOfReferences(Group, ".groups"),
                  default=[], required=False),
        ]

This is similar to previous objects

Now to put it all together, we create a root Object that represents the document:

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

Here we have the same thing describing the root document:

* `version` field is a simple string
* `updates` field is a List of Nodes - where each node is a simple string. 
* `groups`, `users`, and `projects` field are each _KeyBasedList_ - or list of objects mapped by 
  their identity. The difference between _KeyBasedList_ and _SchemeNode_ is that all child nodes
  are of the same type and all keys are identities of those nodes.
* In addition, we define a few more properties for this node:
    * `PRESERVE_ORDER` suggests to attempt to preserve the order of the keys in this object
    * `ALLOW_UNDEFINED` tells the parser that if it encounters a key that in not a defined field,
      store it as a plain value. If not set to _True_, QuickScheme will throw an exception


### Usage Reference


#### Node Types

Currently implemented Node Types:

* ***SchemaNode*** - A basic mapping with pre-defined fields.
    * ***Options***
        * `FIELDS` - a list of Fields (see Fields bellow)
        * `ALLOW_UNDEFINED`(Default: False) - if true, store fields that are not defined
        * `MAP_CLASS` (Default: None) if set, force use of this _dict_ subclass.
        * `PRESERVE_ORDER` (Default: False) if set to true, attempt to preserve order of fields
        * `BRIEF_OUT` (Default: False) - if set to true, attempt to use brief format if brief
          field exists and is the only field that is set

* ***KeyBasedListNode*** - A list of nodes presented as a mapping, where all nodes are of the same
  type, and the key in the mapping is the identity field for each node.
    * ***Options***
        * `TYPE` - type of nodes contained in this list
    * ***Helper Functions***
        * ***KeyBasedList(item_type)*** generates a ***KeyBasedListNode*** class with TYPE set to 
          `item_type`. For example, to create a list of ***Group*** nodes keyed by their id, use 
            `KeyBasedList(Group)`

* ***ListOfNodesNode*** - Basic sequence of items (list or array) where each of the items is of same
  type
    * ***Options***
        * `TYPE` - type of nodes contained in this List
    * ***Helper Functions***
        * ***ListOfNodes(item_type)*** generates a ListOfNodesNode with TYPE set to `item_type`.
          For example, to create a list of ***Group*** nodes use `ListOfNodes(Group)`

* ***ReferenceNode*** - A Node that stores an ID that references another node stored in 
  ***KeyBasedListNode*** object somewhere in document
    * ***Options***
        * `PATH` - Path to the ***KeyBasedListNode*** in the document. Path uses '.' as separator.
        * `DEREFERENCE` - (Default: True) If set to true, dereference the item on conversion to
          data. If False, then when converting to data, return only the id field.
    * ***Helper Functions***
        * ***ListOfNodes(item_type)*** generates a ListOfNodesNode with TYPE set to `item_type`.
          For example, to create a list of ***Group*** nodes use `ListOfNodes(Group)`

#### Fields

Definitions of key-based fields

* ***Field(name, [options])*** Basic field definition
    * Options:
        * `name` - (_string_) name of the field key in the parent
        * `ftype` - (_Class_) - Field Type. Default is string May be any class that can be
          initialized  with the data or a derivative of `SchemeBaseNode`
        * `required` - (_bool_) - If true, this field must be specified explicitly.)
        * `default` - (_string_ or _callable_) - If specified, value to use if field is not
          specified. If value is a callable, it is executed with the object as argument 
        * `identity` - (_bool_) - if true, this fields is set when identity is set. By default, only
          one identity field is allowed to be present.
        * `brief` - (_bool_) - if True, this field is set when "brief" format (i.e. specifying
          value) as a value instead of a mapping) - By default only one brief field is allowed. If
          more complicated processing is required, do not set this field and instead implement
          `_brief_set(data)` method in your class deriving from `SchemeNode`
        * `always` - (_bool_) - If _true_(default) show this field when asking for data  even if
          not set. If _false_ only show if explicitly set
        * `validator` - (_callable_) - If provided, called to validate this field. Must take 
          `FieldValue` object as first parameter

## TODOS:

Things that may be documented but not yet implemented or are in works:

(right now this is a very open list, many things are not yet done)

* `Node` specifications
    * ???

* `Field` specifications
    * ???
