:mod:`internal`
======================

.. module:: rx.internal
   :synopsis: Default functions and helper classes.

.. method:: noop(*args, **kwargs)

	pass

.. method:: identity(x)

	Returns x

.. method:: defaultEquals(x, y)

	Returns ``x == y``

.. method:: defaultCompareTo(x, y)

	Returns
	* 1 	if x > y
	* 0 	if x == y
	* -1 	otherwise

.. method:: defaultError(error, *args, **kwargs)

	``raise error``