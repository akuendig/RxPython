:mod:`disposable`
=================

.. module:: rx.disposable
   :synopsis: Disposable implementations.

.. **Source code:** :source:`rx/disposable.py`

All Disposables implement the :class:`Disposable` interface which requires from them only a :meth:`dispose` method.
The abstract base class that all :class:`Disposable` classes inherit from is :class:`Cancelable` which provides the
property :attr:`isDisposed` to check if a :class:`Disposable` has already been disposed.

.. autoclass:: Disposable

   .. method:: dispose()

      Disposes the current object. It is assumed from all classes that implement
      :meth:`dispose`, that the mothod can be called multiple times with the
      side effect of disposing only occuring once.

   .. staticmethod:: create(action)

      :meth:`create` returns a :class:`Cancelable` that calls ``action`` at the first
      call to :meth:`dispose`.

   .. staticmethod:: empty()

      :meth:`empty` returns a :class:`Disposable` that does nothing on :meth:`dispose`.

.. autoclass:: Cancelable
   :members:

.. autoclass:: AnonymouseDisposable

   .. attribute:: isDisposed

      Returns True if :meth:`dispose` was called at least once.

.. autoclass:: BooleanDisposable
   :members:

.. autoclass:: CompositeDisposable

   .. method:: add(disposable)

      Adds ``disposable`` to the :class:`CompositeDisposable` and disposes
      ``disposable`` if it is already disposed.

   .. method:: contains(disposable)

      Returns True if the ``disposable`` is contained in the
      :class:`CompositeDisposable`.

   .. method:: remove(disposable)

      Removes the ``disposable`` from the :class:`CompositeDisposable` and
      disposes it. Returns False if ``disposable`` has not been found
      otherwise True.

   .. method:: clear()

      Removes all disposables from the :class:`CompositeDisposable`
      and disposes them.

.. autoclass:: RefCountDisposable

.. autoclass:: SchedulerDisposable

   .. method:: getDisposable()

      Returns a :class:`Disposable` that has a reference to this instance.

.. autoclass:: SerialDisposable

   .. attribute:: disposable

      The current :class:`Disposable`. Assigning a new :class:`Disposable`
      disposes the current :class:`Disposable` and sets the new as the current.

.. autoclass:: SingleAssignmentDisposable

   .. attribute:: disposable

      The current :class:`Disposable`. Assigning this property more than
      once raises an Exception.
