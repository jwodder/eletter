.. currentmodule:: eletter

API
===

The `compose()` Function
------------------------

.. autofunction:: compose

Addresses
---------

Addresses in ``eletter`` can be specified in three ways:

- As an ``"address@domain.com"`` string giving just a bare e-mail address

- As an ``eletter.Address("Display Name", "address@domain.com")`` instance
  pairing a person's name with an e-mail address

- As an ``eletter.Group("Group Name", iterable_of_addresses)`` instance
  specifying a group of addresses (strings or ``Address`` instances)

.. note::

    `eletter.Address` and `eletter.Group` are actually just subclasses of
    `~email.headerregistry.Address` and `~email.headerregistry.Group` from
    `email.headerregistry` with slightly more convenient constructors.  You can
    also use the standard library types directly, if you want to.

.. autoclass:: Address
.. autoclass:: Group

`MailItem` Classes
------------------

.. autoclass:: MailItem()
    :exclude-members: content_id

.. _attachments:

Attachments
~~~~~~~~~~~

.. autoclass:: Attachment()
    :no-members:

.. autoclass:: BytesAttachment
    :exclude-members: DEFAULT_CONTENT_TYPE, compose
    :inherited-members:

.. autoclass:: EmailAttachment
    :exclude-members: compose
    :inherited-members:

.. autoclass:: TextAttachment
    :exclude-members: DEFAULT_CONTENT_TYPE, compose
    :inherited-members:


Body Classes
~~~~~~~~~~~~

.. autoclass:: HTMLBody
    :exclude-members: compose
    :inherited-members:

.. autoclass:: TextBody
    :exclude-members: compose
    :inherited-members:


Multipart Classes
~~~~~~~~~~~~~~~~~

.. autoclass:: Multipart()
    :no-members:

.. autoclass:: Alternative
    :exclude-members: compose, clear, count, index
    :inherited-members:

.. autoclass:: Mixed
    :exclude-members: compose, clear, count, index
    :inherited-members:

.. autoclass:: Related
    :exclude-members: compose, clear, count, index
    :inherited-members:


Decomposition
-------------

.. autofunction:: decompose
.. autofunction:: decompose_simple
.. autoclass:: Eletter()
    :member-order: bysource
.. autoclass:: SimpleEletter()
    :member-order: bysource


Exceptions
----------

.. autoexception:: eletter.errors.Error
    :show-inheritance:
.. autoexception:: eletter.errors.DecompositionError
    :show-inheritance:
.. autoexception:: eletter.errors.SimplificationError
    :show-inheritance:
.. autoexception:: eletter.errors.MixedContentError
    :show-inheritance:


Utility Functions
-----------------

.. autofunction:: assemble_content_type
.. autofunction:: format_addresses
.. autofunction:: reply_quote
