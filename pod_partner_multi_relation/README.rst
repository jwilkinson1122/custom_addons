=========================
Partner Multi Relations
=========================

This module aims to provide generic means to model relations between partners.

Examples would be 'is sibling of' or 'is friend of', but also 'has contract X
with' or 'is assistant of'. This way, you can encode your knowledge about your
partners directly in your partner list.

Usage
=====

Relation Types
~~~~~~~~~~~~~~

Before being able to use relations, you'll have define some first.
Do that in Contacts / Relations / Partner relations.

A relation type has a name for both sides.

To have an assistant-relation, you would name one side 'is assistant of' and the other side 'has assistant'.

Partner Types
~~~~~~~~~~~~~

The `Partner Type` fields allow to constrain what type of partners can be used
on the left and right sides of the relation.

* In the example above, the assistant-relation only makes sense between people, so you would choose 'Person' for both partner types.
* For a relation 'is a competitor of', both sides would be companies.
* A relation 'has worked for' should have persons on the left side and companies on the right side.

If you leave these fields empty, the relation is applicable to all types of partners.

Partner Categories
~~~~~~~~~~~~~~~~~~

You may use categories (tags) to further specify the type of partners.

You could for example enforce the 'is member of' relation to accept only companies with the label 'Organization' on the right side.

Reflexive
~~~~~~~~~

A reflexive relation type allows a partner to be in relation with himself.

* The CEO of a company could be his own manager.

Symmetric
~~~~~~~~~

A symetric relation has the same value for the left and right sides.

For example, in a competitor relation, both companies are competitors of each other.


Invalid Relation Handling
~~~~~~~~~~~~~~~~~~~~~~~~~

When the configuration of a relation type changes, some relations between 2 partners may become invalid.

For example, if the left partner type is set to `Person` and a relation already exists with a company on the right side,
that relation becomes invalid.

What happens with invalid relations is customizable on the relation type.

4 possible behaviors are available:

* Do not allow change that will result in invalid relations
* Allow existing relations that do not fit changed conditions
* End relations per today, if they do not fit changed conditions
* Delete relations that do not fit changed conditions

Searching Partners With Relations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To search for existing relations, go to `Contacts / Relations / Relations`.

To find all assistants in your database, fill in 'assistant' and
autocomplete will propose to search for this type of relation.

Now if you want to find Colleen's assistant, you fill in 'Colleen' and one of the proposals
is to search for partners having a relation with Colleen.

Searching Relations From Partner View
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A smart button is available on the partner form view to display the list of relations.
