:mod:`observer`
======================

.. module:: rx.observer
   :synopsis: Observer implementations.

.. **Source code:** :source:`rx/observer.py`

Observers are the main receivers of notification in rx. Every :class:`Observer`
has an :meth:`onNext`, an :meth:`onError` and an :meth:`onCompleted` method.
An :class:`Observer` is also a :class:`rx.disposable.Disposable`.

.. autoclass:: Observer
	:members:

	.. staticmethod:: create(onNext=None, onError=None, onCompleted=None)

		Creates and returns an :class:`Observer`. The default for :meth:`onNext`
		is to ignore the value, the default for :meth:`onError` is to raise the
		error, the default for :meth:`onCompleted` is to ignore the notification.

	.. staticmethod:: synchronize(observer, lock=None)

		Returns a synchronized :class:`Observer` that aquires the ``lock``
		before either :meth:`onNext`, :meth:`onError` or :meth:`onCompleted`
		get called. If no lock is provided, a new :class:`RLock` is used as default.

	.. staticmethod:: fromNotifier(handler)

		Returns an :class:`Observer`, that wraps the ``handler``. The handler gets
		called with :class:`rx.notification.Notification` instances representing
		the events that happend.

	.. method:: toNotifier

		Returns a function that accepts :class:`rx.notification.Notification`
		objects and calls their :meth:`accept` method with self as the parameter.

	.. method:: asObserver

		Returns an :class:`Observer` to hide the type of the original :class:`Observer`.

	.. method:: checked

		Returns an :class:`Observer` that checks if :meth:`onError`
		or :meth:`onCompleted` have already been called and if so,
		raises an Exception.

	.. method:: onNext(value)

		The method that gets called whenever a value was produced
		by the :class:`rx.observable.Observable`.

	.. method:: onError(exception)

		The method that gets called when an error occured in the
		:class:`rx.observable.Observable`. After an error an
		:class:`rx.observable.Observable` is regarded as closed and
		does not produce any further calls to :meth:`onNext`,
		:meth:`onError`, or :meth:`onCompleted`.

	.. method:: onCompleted(value)

		The method that gets called when the
		:class:`rx.observable.Observable` finished. After completion an
		:class:`rx.observable.Observable` is regarded as closed and
		does not produce any further calls to :meth:`onNext`,
		:meth:`onError`, or :meth:`onCompleted`.

	.. method:: dispose()

		Disposes this observer to not receive any further onNext, onError
		or onCompleted calls.
