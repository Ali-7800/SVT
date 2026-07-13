from typing import Any
import inspect
import numpy as np
from numbers import Real, Integral


def sf(x, precision=3):
    if precision is not None:
        x = float(
            np.format_float_positional(
                x, precision=precision, unique=False, fractional=False, trim="k"
            )
        )
    return x


def _wrapped_property(attr, wrapper, default):
    """Property that stores its value as `wrapper(value)` under `_<attr>`,
    and resets to `wrapper(default)` on delete."""
    private = f"_{attr}"

    def getter(self):
        return getattr(self, private)

    def setter(self, value):
        setattr(self, private, wrapper(value))

    def deleter(self):
        setattr(self, private, wrapper(default))

    return property(getter, setter, deleter)


def _bool_property(attr, default=False):
    """Strictly-boolean property (used for the `metallic` flags)."""
    private = f"_{attr}"

    def getter(self):
        return getattr(self, private)

    def setter(self, value):
        if not isinstance(value, bool):
            raise TypeError(f"{attr} property must either be True or False")
        setattr(self, private, value)

    def deleter(self):
        setattr(self, private, default)

    return property(getter, setter, deleter)


_VALID_MAP_SUFFIXES = (
    ".gif",
    ".png",
    ".tga",
    ".iff",
    ".ppm",
    ".pgm",
    ".jpg",
    ".sys",
    "",
)


def _extension_from_path(value, kind):
    """Validate an image/bump map path and return the POV-Ray extension
    keyword for it (e.g. 'png', 'jpeg'). `kind` ('image map' / 'bump map')
    is only used to phrase error messages."""
    if not isinstance(value, str):
        raise TypeError(f"{kind} path must be a string")
    if not (value[-4:] in _VALID_MAP_SUFFIXES or value[-5:] == ".jpeg"):
        raise ValueError(
            f"{kind} extension must be one of the following: "
            "gif, jpg, jpeg, png, tga, iff, ppm, pgm, sys"
        )
    if value[-5:] == ".jpeg" or value[-4:] == ".jpg":
        return "jpeg"
    return value[-3:]


class TimeCallable:
    """
    Wrap an array-like object or a callable as a function of time.

    If initialized with an iterable, the object is converted into a function
    that always returns the same value regardless of the input time.

    If initialized with a callable, the callable must accept exactly one
    argument (time) and return an object satisfying :meth:`shape_condition`.

    Subclasses can override :meth:`shape_condition` to enforce additional
    constraints on the returned object.

    Parameters
    ----------
    input_array : iterable or callable
        Either

        - an iterable that is returned unchanged for every time value, or
        - a callable ``f(time)`` returning an iterable.
    """

    def __init__(self, input_array) -> None:
        self.array = input_array

        if self._callable_condition(input_array):
            output = input_array(0)

            if not self.shape_condition(output):
                raise ValueError(
                    "Callable returned an invalid object: "
                    f"{self.shape_condition_error(output)}"
                )

            self._callable_array = input_array

        else:
            try:
                if not self.shape_condition(input_array):
                    raise ValueError(
                        "Input object is invalid: "
                        f"{self.shape_condition_error(input_array)}"
                    )

                self._callable_array = self._make_array_function(input_array)

            except TypeError as exc:
                raise TypeError(
                    "input_array must be either an iterable or a callable "
                    "accepting a single argument (time)."
                ) from exc

    def __call__(self, time: float) -> Any:
        """Evaluate the array at the given time."""
        return self._callable_array(time)

    @staticmethod
    def _make_array_function(array):
        """Create a constant function that always returns ``array``."""

        def array_function(_):
            return array

        return array_function

    @staticmethod
    def _callable_condition(obj) -> bool:
        """
        Return True if ``obj`` is callable and accepts exactly one argument.
        """
        if not callable(obj):
            return False

        try:
            inspect.signature(obj).bind(None)
            return True
        except TypeError:
            return False

    def shape_condition_error(self, array) -> str:
        """
        Return a description of why ``shape_condition`` failed.

        Subclasses can override this to provide more informative error
        messages. This method is only called when ``shape_condition()``
        returns False.
        """
        return "Object does not satisfy shape_condition()."

    def shape_condition(self, array) -> bool:
        """
        Check whether the returned object satisfies the required shape.

        Subclasses should override this method to implement application-
        specific validation.

        Parameters
        ----------
        array
            Object returned by the callable or provided directly during
            initialization.

        Returns
        -------
        bool
            True if the object satisfies the required shape.
        """
        return True


class TimeVecN(TimeCallable):
    """Time-dependent N-dimensional vector."""

    def __init__(self, input_array, n: int = 3) -> None:
        self.n = n
        super().__init__(input_array)

    def shape_condition(self, array) -> bool:
        """
        Return True if ``array`` is an iterable containing exactly ``n``
        real-valued components.
        """
        try:
            return len(array) == self.n and all(isinstance(x, Real) for x in array)
        except TypeError:
            # Object is not iterable or has no length.
            return False

    def shape_condition_error(self, array) -> str:
        """
        Return a descriptive error explaining why ``array`` is not a valid
        N-dimensional vector.
        """
        try:
            length = len(array)
        except TypeError:
            return (
                f"Expected an iterable of length {self.n} containing real "
                f"numbers, but received an object of type "
                f"'{type(array).__name__}'."
            )

        if length != self.n:
            return (
                f"Expected an iterable of length {self.n}, "
                f"but received one of length {length}."
            )

        non_numeric = [
            f"index {i} ({type(v).__name__})"
            for i, v in enumerate(array)
            if not isinstance(v, Real)
        ]

        if non_numeric:
            return (
                "Expected all elements to be real numbers, but found "
                + ", ".join(non_numeric)
                + "."
            )

        return f"Object is not a valid {self.n}-dimensional vector."


class TimeVecMN(TimeCallable):
    """Time-dependent M×N array."""

    def __init__(self, input_array, m=3) -> None:
        self.m = m
        super().__init__(input_array)

    def shape_condition(self, array) -> bool:
        """
        Return True if ``array`` is a M×N array-like object whose entries are
        all real numbers.
        """
        try:
            if len(array) != self.m:
                return False

            n = len(array[0])

            return all(len(row) == n for row in array) and all(
                isinstance(value, Real) for row in array for value in row
            )
        except TypeError:
            # Not iterable or not 2-dimensional.
            return False

    def shape_condition_error(self, array) -> str:
        """
        Return a descriptive error explaining why ``array`` is not a valid
        M×N array.
        """
        try:
            n_rows = len(array)
        except TypeError:
            return (
                f"Expected a {self.m}×N iterable of real numbers, but received an "
                f"object of type '{type(array).__name__}'."
            )

        if n_rows != 3:
            return f"Expected an iterable with 3 rows, but received {n_rows}."

        try:
            row_lengths = [len(row) for row in array]
        except TypeError:
            return "Each row must itself be an iterable."

        if len(set(row_lengths)) != 1:
            return (
                "All rows must have the same length, but received row "
                f"lengths {row_lengths}."
            )

        for i, row in enumerate(array):
            for j, value in enumerate(row):
                if not isinstance(value, Real):
                    return (
                        "Expected all elements to be real numbers, but found "
                        f"{type(value).__name__} at index ({i}, {j})."
                    )

        return f"Object is not a valid {self.m}×N array."


class TimeScalar(TimeCallable):
    """Time-dependent scalar."""

    def __init__(self, input_value) -> None:
        super().__init__(input_value)

    def shape_condition(self, value) -> bool:
        """
        Return True if ``value`` is a real number.
        """
        return isinstance(value, Real)

    def shape_condition_error(self, value) -> str:
        """
        Return a descriptive error explaining why ``value`` is not a valid
        scalar.
        """
        return (
            f"Expected a real number, but received an object of type "
            f"'{type(value).__name__}'."
        )


class TimeIndexN(TimeCallable):
    """Time-dependent N-dimensional index vector."""

    def __init__(self, input_array, n: int = 3) -> None:
        self.n = n
        super().__init__(input_array)

    def shape_condition(self, array) -> bool:
        """
        Return True if ``array`` is an iterable containing exactly ``n``
        integer components.
        """
        try:
            return len(array) == self.n and all(isinstance(x, Integral) for x in array)
        except TypeError:
            # Object is not iterable or has no length.
            return False

    def shape_condition_error(self, array) -> str:
        """
        Return a descriptive error explaining why ``array`` is not a valid
        N-dimensional index vector.
        """
        try:
            length = len(array)
        except TypeError:
            return (
                f"Expected an iterable of length {self.n} containing integer "
                f"numbers, but received an object of type "
                f"'{type(array).__name__}'."
            )

        if length != self.n:
            return (
                f"Expected an iterable of length {self.n}, "
                f"but received one of length {length}."
            )

        non_numeric = [
            f"index {i} ({type(v).__name__})"
            for i, v in enumerate(array)
            if not isinstance(v, Integral)
        ]

        if non_numeric:
            return (
                "Expected all elements to be integer numbers, but found "
                + ", ".join(non_numeric)
                + "."
            )

        return f"Object is not a valid {self.n}-dimensional vector."


class TimeIndexMN(TimeCallable):
    """Time-dependent M×N index array."""

    def __init__(self, input_array, m) -> None:
        self.m = m
        super().__init__(input_array)

    def shape_condition(self, array) -> bool:
        """
        Return True if ``array`` is a M×N array-like object whose entries are
        all integer numbers.
        """
        try:
            if len(array) != self.m:
                return False

            n = len(array[0])

            return all(len(row) == n for row in array) and all(
                isinstance(value, Integral) for row in array for value in row
            )
        except TypeError:
            # Not iterable or not 2-dimensional.
            return False

    def shape_condition_error(self, array) -> str:
        """
        Return a descriptive error explaining why ``array`` is not a valid
        M×N array.
        """
        try:
            n_rows = len(array)
        except TypeError:
            return (
                f"Expected a {self.m}×N iterable of integer numbers, but received an "
                f"object of type '{type(array).__name__}'."
            )

        if n_rows != self.m:
            return f"Expected an iterable with m rows, but received {n_rows}."

        try:
            row_lengths = [len(row) for row in array]
        except TypeError:
            return "Each row must itself be an iterable."

        if len(set(row_lengths)) != 1:
            return (
                "All rows must have the same length, but received row "
                f"lengths {row_lengths}."
            )

        for i, row in enumerate(array):
            for j, value in enumerate(row):
                if not isinstance(value, Integral):
                    return (
                        "Expected all elements to be integer numbers, but found "
                        f"{type(value).__name__} at index ({i}, {j})."
                    )

        return f"Object is not a valid {self.m}×N array."
