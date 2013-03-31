:mod:`subject`
======================

.. module:: rx.subject
   :synopsis: Subject implementations.

.. **Source code:** :source:`rx/observer.py`

Subjects are :class:`rx.observer.Observer` and :class:`rx.observable.Observable`
at the same time. Whenever you need an explicit object that you can pass on as
:class:`rx.observable.Observable` but need to manualy call the onNext, onError and
onCompleted methods of the :class:`rx.observable.Observable` then you need a
:class:`Subject`.

It is recommended to create an :class:`rx.observable.Observable` by
using :meth:`rx.observable.Observable.create`,  :meth:`rx.observable.Observable.fromEvent`,
:meth:`rx.observable.Observable.fromFuture`, :meth:`rx.observable.Observable.generate` and so
on.


.. class:: Subject

	.. method:: onNext(value)

		Calls the onNext method on all observers of this Subject.

	.. method:: onError(exception)

		Calls the onError method on all observers of this Subject.

	.. method:: onCompleted()

		Calls the onCompleted method on all observers of this Subject.

	.. method:: subscribe(observer)
				subscribe(onNext[, onError=None[, onCompleted=none]])

		See :meth:`rx.observable.Observable.subscribe`

	.. method:: dispose()

		See :meth:`rx.observer.Observer.dispose`

	.. staticmethod:: create(observer, observable)

		Return a new :class:`Subject` connecting the ``observable``
		and the ``observer``.

	.. staticmethod:: synchronize(subject, scheduler=None)

		Returns a new :class:`Subject` that synchonizes the call to
		the observers onNext methods. If a ``scheduler`` is provided,
		the values are observed on that :class:`rx.scheduler.Scheduler`.


.. class:: AsyncSubject

	An AsyncSubject does remember the value from its last onNext call.
	Subscribers get either this value or wait for the onCompleted call
	if it has not happend.

	If onError gets called, the subject stops waiting for the onCompleted and
	instead propagates the error to all current and future observers.

	If onCompleted gets called, the subject stops waiting for the onCompleted and
	calls onNext(lastValue) on all current and future observers.


.. class:: BehaviorSubject(initialValue)

	A BehaviorSubject does remember the value from its most recent onNext call.
	Subscribers get the current value on subscription and any firther updates
	via onNext. If no onNext call happend, the observers receive the initial
	value instead.

	If onError gets called, the subject stops propagating value updates and
	instead propagates the error to all current and future observers.

	If onCompleted gets called, the subject stops propagating value updates and
	instead propagates onCompleted() to all current and future observers.

	.. attribute:: hasObservers

		Returns True if any :class:`rx.observer.Observer` has subscribed.
