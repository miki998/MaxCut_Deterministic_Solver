import sys
import ctypes as _c
import signal
import platform
import os
import inspect
import time
import array
import numbers

########


__version__ = "9.5"
__author__ = "LocalSolver"
__copyright__ = "Copyright LocalSolver, all rights reserved"
__email__ = "contact@localsolver.com"
__status__ = "Production"
__all__ = [
    "LSError", "LSState", "LSSolutionStatus", "LSObjectiveDirection",
    "LSCallbackType", "LSOperator", "LSErrorCode", "LSArray", "LSError",
    "LSModel", "LSSolution", "LSStatistics", "LSExpression",
    "LSExternalContext", "LSParam", "LocalSolver", "LSCollection",
    "LSInconsistency", "LSPhase", "LSVersion", "version"
]


########

class LSEnumMeta(type):
    def __new__(mcs, name, bases, dico):
        enum_by_name = {}
        enum_by_value = [None for x in dico if x.isupper()]
        dico["_enum_by_name"] = enum_by_name
        dico["_enum_by_value"] = enum_by_value

        enum_class = super(LSEnumMeta, mcs).__new__(mcs, name, bases, dico)
        
        # Now replace members by equivalent enum members...
        for e in dico.items():
            if e[0].isupper():
                member = enum_class.__new__(enum_class)
                member.__dict__["name"] = e[0]
                member.__dict__["value"] = e[1]
                setattr(enum_class, e[0], member)
                enum_by_name[e[0]] = member
                enum_by_value[e[1]] = member

        return enum_class
        
    def __getattr__(cls, name):
        if name in cls.__dict__['_enum_by_name']:
            return cls.__dict__['_enum_by_name']
        raise AttributeError(name)

    def __setattr__(cls, name, value):
        if name in cls.__dict__['_enum_by_name']:
            raise AttributeError("Cannot reassign LSEnum members.")
        super(LSEnumMeta, cls).__setattr__(name, value)

    def __delattr__(cls, name):
        if name in cls.__dict__['_enum_by_name']:
            raise AttributeError("Cannot delete LSEnum members.")
        super(LSEnumMeta, cls).__setattr__(name, value)

    def __len__(cls):
        return len(cls.__dict__["_enum_by_name"])

    def __str__(cls):
        return str([x.name for x in cls.__dict__["_enum_by_value"] if x != None])

    def __getitem__(cls, pos):
        return cls.__dict__["_enum_by_value"][pos]

    def __iter__(cls):
        return cls.__dict__["_enum_by_value"].__iter__()

    def __repr__(cls):
        return "<LSEnum %r>" % cls.__name__


def ls_with_metaclass(meta, *bases):
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})


class LSEnum(ls_with_metaclass(LSEnumMeta, object)):
    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self.name, self.value)

    def __str__(self):
        return "%s.%s" % (self.__class__.__name__, self.name)

    def __hash__(self):
        return hash(self.__dict__["name"])

    def __setattr__(self):
        raise AttributeError

    def __delattr__(self):
        raise AttributeError


########


class LSError(Exception):
    __slots__ = "error_code", "explanation", "file_name", "function_name", "line_number", "message"

    def __init__(self, errcode, explanation, filename, funcname, lineno):
        self.error_code = errcode
        self.explanation = explanation
        self.file_name = filename
        self.function_name = funcname
        self.line_number = lineno
        self.message = "ERROR [function " + funcname + "]: " + explanation

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message



########


class LSContainer(object):
    def __init__(self, colname, lenfunc, getfunc):
        self.colname = colname
        self.lenfunc = lenfunc
        self.getfunc = getfunc

    def __nonzero__(self):
        return True

    def __len__(self):
        return self.lenfunc()

    def __getitem__(self, key):
        if isinstance(key, int) and (key >= self.lenfunc() or key < 0):
            raise IndexError
        return self.getfunc(key)

    def __str__(self):
        return "collection of <" + self.colname + "> containing " + str(self.lenfunc()) + " item(s)"

    def __contains__(self, other):
        for e in self:
            if e == other:
                return True
        return False

    def count(self):
        return self.lenfunc()

    def index(self, other):
        idx = 0
        for e in self:  
            if e == other:
                return True
            idx += 1
        return False


class LSMutableContainer(LSContainer):
    def __init__(self, colname, lenfunc, getfunc, setfunc):
        self.colname = colname
        self.lenfunc = lenfunc
        self.getfunc = getfunc
        self.setfunc = setfunc

    def __setitem__(self, key, value):
        if isinstance(key, int) and key >= self.lenfunc():
            raise IndexError
        return self.setfunc(key, value)


class LSMutableDict(object):
    def __init__(self, colname, getfunc, setfunc):
        self.__dict__["_colname"] = colname
        self.__dict__["_getfunc"] = getfunc
        self.__dict__["_setfunc"] = setfunc

    def __nonzero__(self):
        return True

    def __getitem__(self, key):
        return self._getfunc(key)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __setitem__(self, key, value):
        self._setfunc(key, value)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __str__(self):
        return "collection of <" + self._colname + ">"

########


class LSState(LSEnum):
    MODELING = 0
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3

########


class LSObjectiveDirection(LSEnum):
    MINIMIZE = 0
    MAXIMIZE = 1


########


class LSOperator(LSEnum):
    BOOL = 0
    FLOAT = 1
    CONST = 2
    SUM = 3
    SUB = 4
    PROD = 5
    MAX = 6
    MIN = 7
    EQ = 8
    NEQ = 9
    GEQ = 10
    LEQ = 11
    GT = 12
    LT = 13
    IIF = 14
    NOT = 15
    AND = 16
    OR = 17
    XOR = 18
    ABS = 19
    DIST = 20
    DIV = 21
    MOD = 22
    ARRAY = 23
    AT = 24
    SCALAR = 25
    CEIL = 26
    FLOOR = 27
    ROUND = 28
    SQRT = 29
    LOG = 30
    EXP = 31
    POW = 32
    COS = 33
    SIN = 34
    TAN = 35
    INT = 36
    PIECEWISE = 37
    LIST = 38
    COUNT = 39
    INDEXOF = 40
    PARTITION = 41
    DISJOINT = 42
    EXTERNAL_FUNCTION = 43
    CALL = 44
    LAMBDA_FUNCTION = 45
    ARGUMENT = 46
    RANGE = 47
    CONTAINS = 48
    SET = 49
    BLACKBOX_FUNCTION = 50

########


class LSSolutionStatus(LSEnum):
    INCONSISTENT = 0
    INFEASIBLE = 1
    FEASIBLE = 2
    OPTIMAL = 3

########


class LSErrorCode(LSEnum):
    API = 0
    FILE = 1
    MODEL = 2
    CALLBACK = 3
    LICENSE = 4
    SOLVER = 5
    INTERNAL = 6
    MODELER = 7


########


class LSCallbackType(LSEnum):
    PHASE_STARTED = 0
    PHASE_ENDED = 1
    DISPLAY = 2
    TIME_TICKED = 3
    ITERATION_TICKED = 4

########


_lls = None
_pending_error = None
_chained_signal_handler = {}
_solvers_stack = []
_lib_name = None
_lib_candidates = []

if platform.system() == "Windows": _lib_name = "localsolver95.dll"
elif platform.system() == "Linux": _lib_name = "liblocalsolver95.so"
elif platform.system() == "Darwin": _lib_name = "liblocalsolver95.dylib"
else: raise ImportError("Cannot determine the underlying platform of your Python distribution. "
        + "Please note that LocalSolver is compatible with Windows, Linux and macOS only. "
        + "Any other system is not officialy supported")

# Try two different locations to load the native library:
# 1. The current folder (used, among others, by the python wheel)
# 2. The system folders (delegates the loading behavior to the system)
_lib_candidates.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), _lib_name))
_lib_candidates.append(_lib_name)

_loaded_library = None
for candidate in _lib_candidates:
    try:
        _lls = _c.CDLL(candidate)
        _loaded_library = candidate
        break
    except:
        pass

if _loaded_library == None:
    raise ImportError("Cannot load or find library " + _lib_name + ". Please ensure that LocalSolver is correctly installed on your system")


def _ls_signal_handler(sig, frame):
    global _chained_signal_handler
    global _pending_error
    try:
        if _chained_signal_handler[sig] == signal.SIG_DFL:
            raise KeyboardInterrupt()
        if _chained_signal_handler[sig] != signal.SIG_IGN:
            _chained_signal_handler[sig](sig, frame)
    except:
        if len(_solvers_stack) == 0: raise
        _pending_error = sys.exc_info()[1]
        ptr = _solvers_stack[-1]._solver_ptr
        _ls_interrupt(ptr, _encode_string(repr(_pending_error)), ptr)

def _ls_define_signal_handler(signame):
    if not hasattr(signal, signame): return
    sig = getattr(signal, signame)
    if signal.getsignal(sig) == _ls_signal_handler: return
    _chained_signal_handler[sig] = signal.signal(sig, _ls_signal_handler)

_ls_define_signal_handler("SIGINT")

def _ls_check_errors(result, func, arguments):
    global _pending_error
    if _pending_error != None:
        err = _pending_error
        _pending_error = None
        raise err
    return result

def _ls_python_exception_hook(code, message, filename, funcname, lineno, data):
    global _pending_error
    if _pending_error != None: return
    _pending_error = LSError(
            LSErrorCode[code],
            message.decode('utf-8'),
            filename.decode('utf-8'),
            funcname.decode('utf-8'),
            lineno)

_ls_create_solver = _lls.ls_create_solver
_ls_create_solver.argtypes = []
_ls_create_solver.restype = _c.c_void_p
_ls_create_solver.errcheck = _ls_check_errors

_ls_delete_solver = _lls.ls_delete_solver
_ls_delete_solver.argtypes = [_c.c_void_p]
_ls_delete_solver.restype = None
_ls_delete_solver.errcheck = _ls_check_errors

_ls_state = _lls.ls_state
_ls_state.argtypes = [_c.c_void_p]
_ls_state.restype = _c.c_int
_ls_state.errcheck = _ls_check_errors

_ls_solve = _lls.ls_solve
_ls_solve.argtypes = [_c.c_void_p]
_ls_solve.restype = None
_ls_solve.errcheck = _ls_check_errors

_ls_stop = _lls.ls_stop
_ls_stop.argtypes = [_c.c_void_p]
_ls_stop.restype = None
_ls_stop.errcheck = _ls_check_errors

_ls_interrupt = _lls.ls_interrupt
_ls_interrupt.argtypes = [_c.c_void_p, _c.c_char_p, _c.c_void_p]
_ls_interrupt.restype = None

_ls_save_environment = _lls.ls_save_environment
_ls_save_environment.argtypes = [_c.c_void_p, _c.c_char_p]
_ls_save_environment.restype = None
_ls_save_environment.errcheck = _ls_check_errors

_ls_load_environment = _lls.ls_load_environment
_ls_load_environment.argtypes = [_c.c_void_p, _c.c_char_p]
_ls_load_environment.restype = None
_ls_load_environment.errcheck = _ls_check_errors

_ls_stats = _lls.ls_stats
_ls_stats.argtypes = [_c.c_void_p]
_ls_stats.restype = _c.c_void_p
_ls_stats.errcheck = _ls_check_errors

_ls_params = _lls.ls_params
_ls_params.argtypes = [_c.c_void_p]
_ls_params.restype = _c.c_void_p
_ls_params.errcheck = _ls_check_errors

_ls_best_solution = _lls.ls_best_solution
_ls_best_solution.argtypes = [_c.c_void_p]
_ls_best_solution.restype = _c.c_void_p
_ls_best_solution.errcheck = _ls_check_errors

_ls_to_string = _lls.ls_to_string
_ls_to_string.argtypes = [_c.c_void_p, _c.c_char_p, _c.c_int]
_ls_to_string.restype = _c.c_int
_ls_to_string.errcheck = _ls_check_errors

_ls_compute_iis = _lls.ls_compute_iis
_ls_compute_iis.argtypes = [_c.c_void_p]
_ls_compute_iis.restype = None
_ls_compute_iis.errcheck = _ls_check_errors

_ls_iis_cause = _lls.ls_iis_cause
_ls_iis_cause.argtypes = [_c.c_void_p, _c.c_int]
_ls_iis_cause.restype = _c.c_int
_ls_iis_cause.errcheck = _ls_check_errors

_ls_iis_nb_causes = _lls.ls_iis_nb_causes
_ls_iis_nb_causes.argtypes = [_c.c_void_p]
_ls_iis_nb_causes.restype = _c.c_int
_ls_iis_nb_causes.errcheck = _ls_check_errors

_ls_iis_to_string = _lls.ls_iis_to_string
_ls_iis_to_string.argtypes = [_c.c_void_p, _c.c_char_p, _c.c_int]
_ls_iis_to_string.restype = _c.c_int
_ls_iis_to_string.errcheck = _ls_check_errors

_ls_callback_type = _c.CFUNCTYPE(None, _c.c_void_p, _c.c_int, _c.c_void_p)

_ls_add_callback = _lls.ls_add_callback
_ls_add_callback.argtypes = [_c.c_void_p, _c.c_int, _ls_callback_type, _c.c_void_p]
_ls_add_callback.restype = None
_ls_add_callback.errcheck = _ls_check_errors

_ls_remove_callback = _lls.ls_remove_callback
_ls_remove_callback.argtypes = [_c.c_void_p, _c.c_int, _c.c_void_p]
_ls_remove_callback.restype = _c.c_bool
_ls_remove_callback.errcheck = _ls_check_errors

_ls_remove_callback_2 = _lls.ls_remove_callback_2
_ls_remove_callback_2.argtypes = [_c.c_void_p, _c.c_int, _c.c_void_p, _c.c_void_p]
_ls_remove_callback_2.restype = _c.c_bool
_ls_remove_callback_2.errcheck = _ls_check_errors

_ls_log_writer_type = _c.CFUNCTYPE(None, _c.c_void_p, _c.c_char_p, _c.c_int, _c.c_void_p)

_ls_set_log_writer = _lls.ls_set_log_writer
_ls_set_log_writer.argtypes = [_c.c_void_p, _ls_log_writer_type, _c.c_void_p, _c.c_int]
_ls_set_log_writer.restype = None
_ls_set_log_writer.errcheck = _ls_check_errors
_ls_set_log_writer2 = _lls.ls_set_log_writer
_ls_set_log_writer2.argtypes = [_c.c_void_p, _c.c_void_p, _c.c_void_p, _c.c_int]
_ls_set_log_writer2.restype = None
_ls_set_log_writer2.errcheck = _ls_check_errors

_ls_add_phase = _lls.ls_add_phase
_ls_add_phase.argtypes = [_c.c_void_p]
_ls_add_phase.restype = _c.c_void_p
_ls_add_phase.errcheck = _ls_check_errors

_ls_phase = _lls.ls_phase
_ls_phase.argtypes = [_c.c_void_p, _c.c_int]
_ls_phase.restype = _c.c_void_p
_ls_phase.errcheck = _ls_check_errors

_ls_nb_phases = _lls.ls_nb_phases
_ls_nb_phases.argtypes = [_c.c_void_p]
_ls_nb_phases.restype = _c.c_int
_ls_nb_phases.errcheck = _ls_check_errors

_ls_phase_params = _lls.ls_phase_params
_ls_phase_params.argtypes = [_c.c_void_p]
_ls_phase_params.restype = _c.c_void_p
_ls_phase_params.errcheck = _ls_check_errors

_ls_phase_stats = _lls.ls_phase_stats
_ls_phase_stats.argtypes = [_c.c_void_p]
_ls_phase_stats.restype = _c.c_void_p
_ls_phase_stats.errcheck = _ls_check_errors

_ls_phase_to_string = _lls.ls_phase_to_string
_ls_phase_to_string.argtypes = [_c.c_void_p, _c.c_char_p, _c.c_int]
_ls_phase_to_string.restype = _c.c_int
_ls_phase_to_string.errcheck = _ls_check_errors

_ls_attrs_is_defined = _lls.ls_attrs_is_defined
_ls_attrs_is_defined.argtypes = [_c.c_void_p, _c.c_char_p]
_ls_attrs_is_defined.restype = _c.c_bool
_ls_attrs_is_defined.errcheck = _ls_check_errors

_ls_attrs_type = _lls.ls_attrs_type
_ls_attrs_type.argtypes = [_c.c_void_p, _c.c_char_p]
_ls_attrs_type.restype = _c.c_int
_ls_attrs_type.errcheck = _ls_check_errors

_ls_attrs_get_bool = _lls.ls_attrs_get_bool
_ls_attrs_get_bool.argtypes = [_c.c_void_p, _c.c_char_p]
_ls_attrs_get_bool.restype = _c.c_bool
_ls_attrs_get_bool.errcheck = _ls_check_errors

_ls_attrs_set_bool = _lls.ls_attrs_set_bool
_ls_attrs_set_bool.argtypes = [_c.c_void_p, _c.c_char_p, _c.c_bool]
_ls_attrs_set_bool.restype = None
_ls_attrs_set_bool.errcheck = _ls_check_errors

_ls_attrs_get_int = _lls.ls_attrs_get_int
_ls_attrs_get_int.argtypes = [_c.c_void_p, _c.c_char_p]
_ls_attrs_get_int.restype = _c.c_int
_ls_attrs_get_int.errcheck = _ls_check_errors

_ls_attrs_set_int = _lls.ls_attrs_set_int
_ls_attrs_set_int.argtypes = [_c.c_void_p, _c.c_char_p, _c.c_int]
_ls_attrs_set_int.restype = None
_ls_attrs_set_int.errcheck = _ls_check_errors

_ls_attrs_get_llong = _lls.ls_attrs_get_llong
_ls_attrs_get_llong.argtypes = [_c.c_void_p, _c.c_char_p]
_ls_attrs_get_llong.restype = _c.c_longlong
_ls_attrs_get_llong.errcheck = _ls_check_errors

_ls_attrs_set_llong = _lls.ls_attrs_set_llong
_ls_attrs_set_llong.argtypes = [_c.c_void_p, _c.c_char_p, _c.c_longlong]
_ls_attrs_set_llong.restype = None
_ls_attrs_set_llong.errcheck = _ls_check_errors

_ls_attrs_get_double = _lls.ls_attrs_get_double
_ls_attrs_get_double.argtypes = [_c.c_void_p, _c.c_char_p]
_ls_attrs_get_double.restype = _c.c_double
_ls_attrs_get_double.errcheck = _ls_check_errors

_ls_attrs_set_double = _lls.ls_attrs_set_double
_ls_attrs_set_double.argtypes = [_c.c_void_p, _c.c_char_p, _c.c_double]
_ls_attrs_set_double.restype = None
_ls_attrs_set_double.errcheck = _ls_check_errors

_ls_attrs_get_string = _lls.ls_attrs_get_string
_ls_attrs_get_string.argtypes = [_c.c_void_p, _c.c_char_p, _c.c_char_p, _c.c_int]
_ls_attrs_get_string.restype = _c.c_int
_ls_attrs_get_string.errcheck = _ls_check_errors

_ls_attrs_set_string = _lls.ls_attrs_set_string
_ls_attrs_set_string.argtypes = [_c.c_void_p, _c.c_char_p, _c.c_char_p]
_ls_attrs_set_string.restype = None
_ls_attrs_set_string.errcheck = _ls_check_errors

_ls_attrs_to_string = _lls.ls_attrs_to_string
_ls_attrs_to_string.argtypes = [_c.c_void_p, _c.c_char_p, _c.c_int]
_ls_attrs_to_string.restype = _c.c_int
_ls_attrs_to_string.errcheck = _ls_check_errors

_ls_close = _lls.ls_close
_ls_close.argtypes = [_c.c_void_p]
_ls_close.restype = None
_ls_close.errcheck = _ls_check_errors

_ls_open = _lls.ls_open
_ls_open.argtypes = [_c.c_void_p]
_ls_open.restype = None
_ls_open.errcheck = _ls_check_errors

_ls_is_closed = _lls.ls_is_closed
_ls_is_closed.argtypes = [_c.c_void_p]
_ls_is_closed.restype = _c.c_bool
_ls_is_closed.errcheck = _ls_check_errors

_ls_create_int_constant = _lls.ls_create_int_constant
_ls_create_int_constant.argtypes = [_c.c_void_p, _c.c_longlong]
_ls_create_int_constant.restype = _c.c_int
_ls_create_int_constant.errcheck = _ls_check_errors

_ls_create_double_constant = _lls.ls_create_double_constant
_ls_create_double_constant.argtypes = [_c.c_void_p, _c.c_double]
_ls_create_double_constant.restype = _c.c_int
_ls_create_double_constant.errcheck = _ls_check_errors

_ls_int_native_function_type = _c.CFUNCTYPE(_c.c_longlong, _c.c_void_p, _c.c_void_p, _c.c_void_p)
_ls_double_native_function_type = _c.CFUNCTYPE(_c.c_double, _c.c_void_p, _c.c_void_p, _c.c_void_p)

_ls_create_int_external_function = _lls.ls_create_int_external_function
_ls_create_int_external_function.argtypes = [_c.c_void_p, _ls_int_native_function_type, _c.c_void_p]
_ls_create_int_external_function.restype = _c.c_int
_ls_create_int_external_function.errcheck = _ls_check_errors

_ls_create_double_external_function = _lls.ls_create_double_external_function
_ls_create_double_external_function.argtypes = [_c.c_void_p, _ls_double_native_function_type, _c.c_void_p]
_ls_create_double_external_function.restype = _c.c_int
_ls_create_double_external_function.errcheck = _ls_check_errors

_ls_create_int_blackbox_function = _lls.ls_create_int_blackbox_function
_ls_create_int_blackbox_function.argtypes = [_c.c_void_p, _ls_int_native_function_type, _c.c_void_p]
_ls_create_int_blackbox_function.restype = _c.c_int
_ls_create_int_blackbox_function.errcheck = _ls_check_errors

_ls_create_double_blackbox_function = _lls.ls_create_double_blackbox_function
_ls_create_double_blackbox_function.argtypes = [_c.c_void_p, _ls_double_native_function_type, _c.c_void_p]
_ls_create_double_blackbox_function.restype = _c.c_int
_ls_create_double_blackbox_function.errcheck = _ls_check_errors

_ls_create_expression = _lls.ls_create_expression
_ls_create_expression.argtypes = [_c.c_void_p, _c.c_int]
_ls_create_expression.restype = _c.c_int
_ls_create_expression.errcheck = _ls_check_errors

_ls_create_expression_1 = _lls.ls_create_expression_1
_ls_create_expression_1.argtypes = [_c.c_void_p, _c.c_int, _c.c_int]
_ls_create_expression_1.restype = _c.c_int
_ls_create_expression_1.errcheck = _ls_check_errors

_ls_create_expression_2 = _lls.ls_create_expression_2
_ls_create_expression_2.argtypes = [_c.c_void_p, _c.c_int, _c.c_int, _c.c_int]
_ls_create_expression_2.restype = _c.c_int
_ls_create_expression_2.errcheck = _ls_check_errors

_ls_create_expression_3 = _lls.ls_create_expression_3
_ls_create_expression_3.argtypes = [_c.c_void_p, _c.c_int, _c.c_int, _c.c_int, _c.c_int]
_ls_create_expression_3.restype = _c.c_int
_ls_create_expression_3.errcheck = _ls_check_errors

_ls_create_expression_n = _lls.ls_create_expression_n
_ls_create_expression_n.argtypes = [_c.c_void_p, _c.c_int, _c.c_size_t, _c.c_int]
_ls_create_expression_n.restype = _c.c_int
_ls_create_expression_n.errcheck = _ls_check_errors

_ls_nb_expressions = _lls.ls_nb_expressions
_ls_nb_expressions.argtypes = [_c.c_void_p]
_ls_nb_expressions.restype = _c.c_int
_ls_nb_expressions.errcheck = _ls_check_errors

_ls_nb_constraints = _lls.ls_nb_constraints
_ls_nb_constraints.argtypes = [_c.c_void_p]
_ls_nb_constraints.restype = _c.c_int
_ls_nb_constraints.errcheck = _ls_check_errors

_ls_nb_objectives = _lls.ls_nb_objectives
_ls_nb_objectives.argtypes = [_c.c_void_p]
_ls_nb_objectives.restype = _c.c_int
_ls_nb_objectives.errcheck = _ls_check_errors

_ls_nb_decisions = _lls.ls_nb_decisions
_ls_nb_decisions.argtypes = [_c.c_void_p]
_ls_nb_decisions.restype = _c.c_int
_ls_nb_decisions.errcheck = _ls_check_errors

_ls_nb_operands = _lls.ls_nb_operands
_ls_nb_operands.argtypes = [_c.c_void_p]
_ls_nb_operands.restype = _c.c_int
_ls_nb_operands.errcheck = _ls_check_errors

_ls_constraint = _lls.ls_constraint
_ls_constraint.argtypes = [_c.c_void_p, _c.c_int]
_ls_constraint.restype = _c.c_int
_ls_constraint.errcheck = _ls_check_errors

_ls_add_constraint = _lls.ls_add_constraint
_ls_add_constraint.argtypes = [_c.c_void_p, _c.c_int]
_ls_add_constraint.restype = None
_ls_add_constraint.errcheck = _ls_check_errors

_ls_remove_constraint = _lls.ls_remove_constraint
_ls_remove_constraint.argtypes = [_c.c_void_p, _c.c_int]
_ls_remove_constraint.restype = None
_ls_remove_constraint.errcheck = _ls_check_errors

_ls_remove_constraint_with_expr = _lls.ls_remove_constraint_with_expr
_ls_remove_constraint_with_expr.argtypes = [_c.c_void_p, _c.c_int]
_ls_remove_constraint_with_expr.restype = None
_ls_remove_constraint_with_expr.errcheck = _ls_check_errors

_ls_objective = _lls.ls_objective
_ls_objective.argtypes = [_c.c_void_p, _c.c_int]
_ls_objective.restype = _c.c_int
_ls_objective.errcheck = _ls_check_errors

_ls_objective_direction = _lls.ls_objective_direction
_ls_objective_direction.argtypes = [_c.c_void_p, _c.c_int]
_ls_objective_direction.restype = _c.c_int
_ls_objective_direction.errcheck = _ls_check_errors

_ls_add_objective = _lls.ls_add_objective
_ls_add_objective.argtypes = [_c.c_void_p, _c.c_int, _c.c_int]
_ls_add_objective.restype = None
_ls_add_objective.errcheck = _ls_check_errors

_ls_remove_objective = _lls.ls_remove_objective
_ls_remove_objective.argtypes = [_c.c_void_p, _c.c_int]
_ls_remove_objective.restype = None
_ls_remove_objective.errcheck = _ls_check_errors

_ls_decision = _lls.ls_decision
_ls_decision.argtypes = [_c.c_void_p, _c.c_int]
_ls_decision.restype = _c.c_int
_ls_decision.errcheck = _ls_check_errors

_ls_expression_with_name = _lls.ls_expression_with_name
_ls_expression_with_name.argtypes = [_c.c_void_p, _c.c_char_p]
_ls_expression_with_name.restype = _c.c_int
_ls_expression_with_name.errcheck = _ls_check_errors

_ls_expr_is_objective = _lls.ls_expr_is_objective
_ls_expr_is_objective.argtypes = [_c.c_void_p, _c.c_int]
_ls_expr_is_objective.restype = _c.c_bool
_ls_expr_is_objective.errcheck = _ls_check_errors

_ls_expr_is_decision = _lls.ls_expr_is_decision
_ls_expr_is_decision.argtypes = [_c.c_void_p, _c.c_int]
_ls_expr_is_decision.restype = _c.c_bool
_ls_expr_is_decision.errcheck = _ls_check_errors

_ls_expr_is_constraint = _lls.ls_expr_is_constraint
_ls_expr_is_constraint.argtypes = [_c.c_void_p, _c.c_int]
_ls_expr_is_constraint.restype = _c.c_bool
_ls_expr_is_constraint.errcheck = _ls_check_errors

_ls_expr_operator = _lls.ls_expr_operator
_ls_expr_operator.argtypes = [_c.c_void_p, _c.c_int]
_ls_expr_operator.restype = _c.c_int
_ls_expr_operator.errcheck = _ls_check_errors

_ls_expr_type = _lls.ls_expr_type
_ls_expr_type.argtypes = [_c.c_void_p, _c.c_int]
_ls_expr_type.restype = _c.c_int
_ls_expr_type.errcheck = _ls_check_errors

_ls_expr_subtype = _lls.ls_expr_subtype
_ls_expr_subtype.argtypes = [_c.c_void_p, _c.c_int]
_ls_expr_subtype.restype = _c.c_int
_ls_expr_subtype.errcheck = _ls_check_errors

_ls_expr_attrs = _lls.ls_expr_attrs
_ls_expr_attrs.argtypes = [_c.c_void_p, _c.c_int]
_ls_expr_attrs.restype = _c.c_void_p
_ls_expr_attrs.errcheck = _ls_check_errors

_ls_expr_nb_operands = _lls.ls_expr_nb_operands
_ls_expr_nb_operands.argtypes = [_c.c_void_p, _c.c_int]
_ls_expr_nb_operands.restype = _c.c_int
_ls_expr_nb_operands.errcheck = _ls_check_errors

_ls_expr_operand = _lls.ls_expr_operand
_ls_expr_operand.argtypes = [_c.c_void_p, _c.c_int, _c.c_int]
_ls_expr_operand.restype = _c.c_int
_ls_expr_operand.errcheck = _ls_check_errors

_ls_expr_set_operand = _lls.ls_expr_set_operand
_ls_expr_set_operand.argtypes = [_c.c_void_p, _c.c_int, _c.c_int, _c.c_int]
_ls_expr_set_operand.restype = None
_ls_expr_set_operand.errcheck = _ls_check_errors

_ls_expr_add_operand = _lls.ls_expr_add_operand
_ls_expr_add_operand.argtypes = [_c.c_void_p, _c.c_int, _c.c_int]
_ls_expr_add_operand.restype = None
_ls_expr_add_operand.errcheck = _ls_check_errors

_ls_expr_add_operands = _lls.ls_expr_add_operands
_ls_expr_add_operands.argtypes = [_c.c_void_p, _c.c_int, _c.c_size_t, _c.c_int]
_ls_expr_add_operands.restype = None
_ls_expr_add_operands.errcheck = _ls_check_errors

_ls_expr_name = _lls.ls_expr_name
_ls_expr_name.argtypes = [_c.c_void_p, _c.c_int, _c.c_char_p, _c.c_int]
_ls_expr_name.restype = _c.c_int
_ls_expr_name.errcheck = _ls_check_errors

_ls_expr_set_name = _lls.ls_expr_set_name
_ls_expr_set_name.argtypes = [_c.c_void_p, _c.c_int, _c.c_char_p]
_ls_expr_set_name.restype = None
_ls_expr_set_name.errcheck = _ls_check_errors

_ls_expr_to_string = _lls.ls_expr_to_string
_ls_expr_to_string.argtypes = [_c.c_void_p, _c.c_int, _c.c_char_p, _c.c_int]
_ls_expr_to_string.restype = _c.c_int
_ls_expr_to_string.errcheck = _ls_check_errors

_ls_model_to_string = _lls.ls_model_to_string
_ls_model_to_string.argtypes = [_c.c_void_p, _c.c_char_p, _c.c_int]
_ls_model_to_string.restype = _c.c_int
_ls_model_to_string.errcheck = _ls_check_errors

_ls_int_objective_threshold = _lls.ls_int_objective_threshold
_ls_int_objective_threshold.argtypes = [_c.c_void_p, _c.c_int]
_ls_int_objective_threshold.restype = _c.c_longlong
_ls_int_objective_threshold.errcheck = _ls_check_errors

_ls_double_objective_threshold = _lls.ls_double_objective_threshold
_ls_double_objective_threshold.argtypes = [_c.c_void_p, _c.c_int]
_ls_double_objective_threshold.restype = _c.c_double
_ls_double_objective_threshold.errcheck = _ls_check_errors

_ls_set_int_objective_threshold = _lls.ls_set_int_objective_threshold
_ls_set_int_objective_threshold.argtypes = [_c.c_void_p, _c.c_int, _c.c_longlong]
_ls_set_int_objective_threshold.restype = None
_ls_set_int_objective_threshold.errcheck = _ls_check_errors

_ls_set_double_objective_threshold = _lls.ls_set_double_objective_threshold
_ls_set_double_objective_threshold.argtypes = [_c.c_void_p, _c.c_int, _c.c_double]
_ls_set_double_objective_threshold.restype = None
_ls_set_double_objective_threshold.errcheck = _ls_check_errors

_ls_solution_status = _lls.ls_solution_status
_ls_solution_status.argtypes = [_c.c_void_p]
_ls_solution_status.restype = _c.c_int
_ls_solution_status.errcheck = _ls_check_errors

_ls_solution_clear = _lls.ls_solution_clear
_ls_solution_clear.argtypes = [_c.c_void_p]
_ls_solution_clear.restype = None
_ls_solution_clear.errcheck = _ls_check_errors

_ls_solution_int_objective_bound = _lls.ls_solution_int_objective_bound
_ls_solution_int_objective_bound.argtypes = [_c.c_void_p, _c.c_int]
_ls_solution_int_objective_bound.restype = _c.c_longlong
_ls_solution_int_objective_bound.errcheck = _ls_check_errors

_ls_solution_double_objective_bound = _lls.ls_solution_double_objective_bound
_ls_solution_double_objective_bound.argtypes = [_c.c_void_p, _c.c_int]
_ls_solution_double_objective_bound.restype = _c.c_double
_ls_solution_double_objective_bound.errcheck = _ls_check_errors

_ls_solution_int_value = _lls.ls_solution_int_value
_ls_solution_int_value.argtypes = [_c.c_void_p, _c.c_int]
_ls_solution_int_value.restype = _c.c_longlong
_ls_solution_int_value.errcheck = _ls_check_errors

_ls_solution_double_value = _lls.ls_solution_double_value
_ls_solution_double_value.argtypes = [_c.c_void_p, _c.c_int]
_ls_solution_double_value.restype = _c.c_double
_ls_solution_double_value.errcheck = _ls_check_errors

_ls_solution_buffer_value = _lls.ls_solution_buffer_value
_ls_solution_buffer_value.argtypes = [_c.c_void_p, _c.c_int]
_ls_solution_buffer_value.restype = _c.c_void_p
_ls_solution_buffer_value.errcheck = _ls_check_errors

_ls_solution_is_violated = _lls.ls_solution_is_violated
_ls_solution_is_violated.argtypes = [_c.c_void_p, _c.c_int]
_ls_solution_is_violated.restype = _c.c_bool
_ls_solution_is_violated.errcheck = _ls_check_errors

_ls_solution_is_undefined = _lls.ls_solution_is_undefined
_ls_solution_is_undefined.argtypes = [_c.c_void_p, _c.c_int]
_ls_solution_is_undefined.restype = _c.c_bool
_ls_solution_is_undefined.errcheck = _ls_check_errors

_ls_solution_set_int_value = _lls.ls_solution_set_int_value
_ls_solution_set_int_value.argtypes = [_c.c_void_p, _c.c_int, _c.c_longlong]
_ls_solution_set_int_value.restype = None
_ls_solution_set_int_value.errcheck = _ls_check_errors

_ls_solution_set_double_value = _lls.ls_solution_set_double_value
_ls_solution_set_double_value.argtypes = [_c.c_void_p, _c.c_int, _c.c_double]
_ls_solution_set_double_value.restype = None
_ls_solution_set_double_value.errcheck = _ls_check_errors

_ls_solution_collection_clear = _lls.ls_solution_collection_clear
_ls_solution_collection_clear.argtypes = [_c.c_void_p, _c.c_int]
_ls_solution_collection_clear.restype = None
_ls_solution_collection_clear.errcheck = _ls_check_errors

_ls_solution_collection_add = _lls.ls_solution_collection_add
_ls_solution_collection_add.argtypes = [_c.c_void_p, _c.c_int, _c.c_longlong]
_ls_solution_collection_add.restype = None
_ls_solution_collection_add.errcheck = _ls_check_errors

_ls_buffer_count = _lls.ls_buffer_count
_ls_buffer_count.argtypes = [_c.c_void_p]
_ls_buffer_count.restype = _c.c_int
_ls_buffer_count.errcheck = _ls_check_errors

_ls_buffer_type = _lls.ls_buffer_type
_ls_buffer_type.argtypes = [_c.c_void_p, _c.c_int]
_ls_buffer_type.restype = _c.c_int
_ls_buffer_type.errcheck = _ls_check_errors

_ls_buffer_get_int = _lls.ls_buffer_get_int
_ls_buffer_get_int.argtypes = [_c.c_void_p, _c.c_int]
_ls_buffer_get_int.restype = _c.c_longlong
_ls_buffer_get_int.errcheck = _ls_check_errors

_ls_buffer_get_double = _lls.ls_buffer_get_double
_ls_buffer_get_double.argtypes = [_c.c_void_p, _c.c_int]
_ls_buffer_get_double.restype = _c.c_double
_ls_buffer_get_double.errcheck = _ls_check_errors

_ls_buffer_get_buffer = _lls.ls_buffer_get_buffer
_ls_buffer_get_buffer.argtypes = [_c.c_void_p, _c.c_int]
_ls_buffer_get_buffer.restype = _c.c_void_p
_ls_buffer_get_buffer.errcheck = _ls_check_errors

_ls_buffer_contains_int = _lls.ls_buffer_contains_int
_ls_buffer_contains_int.argtypes = [_c.c_void_p, _c.c_longlong]
_ls_buffer_contains_int.restype = _c.c_bool
_ls_buffer_contains_int.errcheck = _ls_check_errors

_ls_buffer_contains_double = _lls.ls_buffer_contains_double
_ls_buffer_contains_double.argtypes = [_c.c_void_p, _c.c_double]
_ls_buffer_contains_double.restype = _c.c_bool
_ls_buffer_contains_double.errcheck = _ls_check_errors

_ls_buffer_copy_int = _lls.ls_buffer_copy_int
_ls_buffer_copy_int.argtypes = [_c.c_void_p, _c.POINTER(_c.c_longlong), _c.c_int]
_ls_buffer_copy_int.restype = None
_ls_buffer_copy_int.errcheck = _ls_check_errors

_ls_buffer_copy_double = _lls.ls_buffer_copy_double
_ls_buffer_copy_double.argtypes = [_c.c_void_p, _c.POINTER(_c.c_double), _c.c_int]
_ls_buffer_copy_double.restype = None
_ls_buffer_copy_double.errcheck = _ls_check_errors

_ls_buffer_to_string = _lls.ls_buffer_to_string
_ls_buffer_to_string.argtypes = [_c.c_void_p, _c.c_char_p, _c.c_int]
_ls_buffer_to_string.restype = _c.c_int
_ls_buffer_to_string.errcheck = _ls_check_errors

_ls_version_code = _lls.ls_version_code
_ls_version_code.argtypes = []
_ls_version_code.restype = _c.c_int
_ls_version_code.errcheck = _ls_check_errors

_ls_globals = _lls.ls_globals
_ls_globals.argtypes = []
_ls_globals.restype = _c.c_void_p
_ls_globals.errcheck = _ls_check_errors

_ls_exception_callback_type = _c.CFUNCTYPE(None, _c.c_int, _c.c_char_p, _c.c_char_p, _c.c_char_p, _c.c_int, _c.c_void_p)
_ls_set_exception_callback = _lls.ls_set_exception_callback
_ls_set_exception_callback.argtypes = [_ls_exception_callback_type, _c.c_void_p]
_ls_set_exception_callback.restype = None
_exception_callback_ref = _ls_exception_callback_type(_ls_python_exception_hook)
_ls_set_exception_callback(_exception_callback_ref, None)

_ls_check_paused_or_stopped = _lls.ls_check_paused_or_stopped
_ls_check_paused_or_stopped.argtypes = [_c.c_void_p]
_ls_check_paused_or_stopped.restype = _c.c_bool
_ls_check_paused_or_stopped.errcheck = _ls_check_errors

_ls_check_not_running = _lls.ls_check_not_running
_ls_check_not_running.argtypes = [_c.c_void_p]
_ls_check_not_running.restype = _c.c_bool
_ls_check_not_running.errcheck = _ls_check_errors

_ls_check_modeling = _lls.ls_check_modeling
_ls_check_modeling.argtypes = [_c.c_void_p]
_ls_check_modeling.restype = _c.c_bool
_ls_check_modeling.errcheck = _ls_check_errors

_ls_check_stopped = _lls.ls_check_stopped
_ls_check_stopped.argtypes = [_c.c_void_p]
_ls_check_stopped.restype = _c.c_bool
_ls_check_stopped.errcheck = _ls_check_errors

_ls_check_expr_index = _lls.ls_check_expr_index
_ls_check_expr_index.argtypes = [_c.c_void_p, _c.c_int]
_ls_check_expr_index.restype = _c.c_bool
_ls_check_expr_index.errcheck = _ls_check_errors

_ls_check_expr_type = _lls.ls_check_expr_type
_ls_check_expr_type.argtypes = [_c.c_void_p, _c.c_int, _c.c_int]
_ls_check_expr_type.restype = _c.c_bool
_ls_check_expr_type.errcheck = _ls_check_errors

_ls_check_buffer_type = _lls.ls_check_buffer_type
_ls_check_buffer_type.argtypes = [_c.c_void_p, _c.c_int, _c.c_int]
_ls_check_buffer_type.restype = _c.c_bool
_ls_check_buffer_type.errcheck = _ls_check_errors

_ls_check_expr_subtype = _lls.ls_check_expr_subtype
_ls_check_expr_subtype.argtypes = [_c.c_void_p, _c.c_int, _c.c_int]
_ls_check_expr_subtype.restype = _c.c_bool
_ls_check_expr_subtype.errcheck = _ls_check_errors

_ls_check_operator = _lls.ls_check_operator
_ls_check_operator.argtypes = [_c.c_void_p, _c.c_int, _c.c_int]
_ls_check_operator.restype = _c.c_bool
_ls_check_operator.errcheck = _ls_check_errors

_LSVT_BOOL = 1
_LSVT_INT = 2
_LSVT_DOUBLE = 4
_LSVT_ARRAY = 8
_LSVT_COLLECTION = 16
_LSVT_FUNCTION = 32
_LSVT_RANGE = 64

_LSAVT_BOOL = 0
_LSAVT_INT = 1
_LSAVT_LONG_LONG = 2
_LSAVT_DOUBLE = 3
_LSAVT_STRING = 4

global_attrs_ptr = _ls_globals()
_ls_attrs_set_bool(global_attrs_ptr, "fromGilLanguage".encode('utf-8'), True)



########


class LSExternalContext(object):
    __slots__ = "_solver", "_attrs_ptr", "_func_id"

    def __init__(self, solver, func_id):
        self._solver = solver
        self._func_id = func_id
        self._attrs_ptr = _ls_expr_attrs(solver._solver_ptr, func_id)

    def get_lower_bound(self):
        _check_solver(self._solver)
        func_type = _ls_expr_subtype(self._solver._solver_ptr, self._func_id)
        if func_type == _LSVT_INT:
            return _ls_attrs_get_llong(self._attrs_ptr, _encode_string("intLowerBound"))
        elif func_type == _LSVT_DOUBLE:
            return _ls_attrs_get_double(self._attrs_ptr, _encode_string("doubleLowerBound"))
        else:
            raise TypeError("This function does not have a lower bound.")

    def set_lower_bound(self, lower_bound):
        _check_solver(self._solver)
        _ls_check_modeling(self._solver._solver_ptr)
        if isinstance(lower_bound, int):
            _ls_check_expr_subtype(self._solver._solver_ptr, self._func_id, _LSVT_INT)
            _ls_attrs_set_llong(self._attrs_ptr, _encode_string("intLowerBound"), lower_bound)
        else:
            _ls_check_expr_subtype(self._solver._solver_ptr, self._func_id, _LSVT_DOUBLE)
            _ls_attrs_set_double(self._attrs_ptr, _encode_string("doubleLowerBound"), lower_bound)

    def get_upper_bound(self):
        _check_solver(self._solver)
        func_type = _ls_expr_subtype(self._solver._solver_ptr, self._func_id)
        if func_type == _LSVT_INT:
            return _ls_attrs_get_llong(self._attrs_ptr, _encode_string("intUpperBound"))
        elif func_type == _LSVT_DOUBLE:
            return _ls_attrs_get_double(self._attrs_ptr, _encode_string("doubleUpperBound"))
        else:
            raise TypeError("This function does not have an upper bound.")

    def set_upper_bound(self, upper_bound):
        _check_solver(self._solver)
        _ls_check_modeling(self._solver._solver_ptr)
        if isinstance(upper_bound, int):
            _ls_check_expr_subtype(self._solver._solver_ptr, self._func_id, _LSVT_INT)
            _ls_attrs_set_llong(self._attrs_ptr, _encode_string("intUpperBound"), upper_bound)
        else:
            _ls_check_expr_subtype(self._solver._solver_ptr, self._func_id, _LSVT_DOUBLE)
            _ls_attrs_set_double(self._attrs_ptr, _encode_string("doubleUpperBound"), upper_bound)

    def is_nanable(self):
        _check_solver(self._solver)
        _ls_check_expr_subtype(self._solver._solver_ptr, self._func_id, _LSVT_DOUBLE)
        return _ls_attrs_get_bool(self._attrs_ptr, _encode_string("nanable"))

    def set_nanable(self, nanable):
        _check_solver(self._solver)
        _ls_check_modeling(self._solver._solver_ptr)
        _ls_check_expr_subtype(self._solver._solver_ptr, self._func_id, _LSVT_DOUBLE)
        _ls_attrs_set_bool(self._attrs_ptr, _encode_string("nanable"), nanable)

    lower_bound = property(get_lower_bound, set_lower_bound)
    upper_bound = property(get_upper_bound, set_upper_bound)
    nanable = property(is_nanable, set_nanable)

########


_string_buf = _c.create_string_buffer(1024)
_free_operands_bufs = []

def _check_solver(solver):
    if solver._solver_ptr == None:
        raise LSError(LSErrorCode.API, "Cannot perform the asked operation on a deleted environment", "lsutils.py", "_check_solver", -1)

def _check_same_solver(solver1, solver2):
    if solver1 != solver2:
        raise LSError(LSErrorCode.API, "The given element does not belong to the same LocalSolver instance", "lsutils.py", "_check_same_solver", -1)

def _check_readwrite_collection(expr_id):
    if expr_id is None:
        raise LSError(LSErrorCode.API, "This collection is read-only and cannot be modified", "lsutils.py", "_check_readwrite_collection", -1)

def _check_enum(value, enum_type):
    if not (type(value) is enum_type):
        raise TypeError("An enum member of type %s is expected" % enum_type.__name__)

def _encode_string(sstr):
    if sstr == None: return None
    else: return sstr.encode('utf-8')

def _decode_bytes(bbytes):
    if bbytes == None: return None
    else: return bbytes.decode('utf-8')

def _decode_subset_bytes(bbytes, length):
    if bbytes == None: return None
    return bbytes[:length].decode('utf-8')

def _read_string(func):
    global _string_buf
    size = func(_string_buf, len(_string_buf))
    if size > len(_string_buf):
        buf = _c.create_string_buffer(size)
        _string_buf = buf
        size = func(buf, len(buf))
    return _string_buf[:size].decode('utf-8')

def _nb_function_args(callval):
    PYSIG = sys.version_info[0] > 3 or sys.version_info[0] == 3 and sys.version_info[1] >= 3
    if PYSIG:
        signature = inspect.signature(callval)
        return len(signature.parameters)
    else:
        args_def = inspect.getargspec(callval)[0]
        return len(args_def)

def _is_string(val):
    PY2 = sys.version_info[0] == 2
    if PY2: string_type = basestring
    else: string_type = str
    return isinstance(val, string_type)

def _extract_python_number(x):
    if isinstance(x, int):
        return x
    elif isinstance(x, float):
        return x
    elif isinstance(x, numbers.Integral):
        return int(x)
    elif isinstance(x, numbers.Real):
        return float(x)
    else:
        raise TypeError("A number (int, float) or an LSExpression is expected but %s of type %s was found" % (repr(x), repr(type(x))))

def _get_attr_value(attrs_ptr, name):
    attr_type = _ls_attrs_type(attrs_ptr, _encode_string(name))
    if attr_type == _LSAVT_BOOL: return _ls_attrs_get_bool(attrs_ptr, _encode_string(name))
    elif attr_type == _LSAVT_INT: return _ls_attrs_get_int(attrs_ptr, _encode_string(name))
    elif attr_type == _LSAVT_LONG_LONG: return _ls_attrs_get_llong(attrs_ptr, _encode_string(name))
    elif attr_type == _LSAVT_DOUBLE: return _ls_attrs_get_double(attrs_ptr, _encode_string(name))
    elif attr_type == _LSAVT_STRING: return _read_string(lambda buf, x: _ls_attrs_get_string(attrs_ptr, _encode_string(name), buf, x))
    else: raise NotImplementedError

def _set_attr_value(attrs_ptr, name, value):
    attr_type = _ls_attrs_type(attrs_ptr, _encode_string(name))
    if attr_type == _LSAVT_BOOL: _ls_attrs_set_bool(attrs_ptr, _encode_string(name), value)
    elif attr_type == _LSAVT_INT: _ls_attrs_set_int(attrs_ptr, _encode_string(name), value)
    elif attr_type == _LSAVT_LONG_LONG: _ls_attrs_set_llong(attrs_ptr, _encode_string(name), value)
    elif attr_type == _LSAVT_DOUBLE: _ls_attrs_set_double(attrs_ptr, _encode_string(name), value)
    elif attr_type == _LSAVT_STRING: _ls_attrs_set_string(attrs_ptr, _encode_string(name), _encode_string(value))

def _autocreate_expr(solver_ptr, expr):
    if isinstance(expr, LSExpression):
        _check_same_solver(solver_ptr, expr._solver_ptr)
        return expr._expr_id
    elif isinstance(expr, int):
        return _ls_create_int_constant(solver_ptr, expr)
    elif isinstance(expr, float):
        return _ls_create_double_constant(solver_ptr, expr)
    else:
        x = _extract_python_number(expr)
        if isinstance(x, int): return _ls_create_int_constant(solver_ptr, x)
        else: return _ls_create_double_constant(solver_ptr, x)

def _fill_operands_buffer(solver_ptr, operands):
    global _free_operands_bufs
    operands_buf = None
    if len(_free_operands_bufs) > 0:
        operands_buf = _free_operands_bufs.pop()
    else:
        operands_buf = array.array('i')
    operands_buf.extend(map(lambda op: _autocreate_expr(solver_ptr, op), operands))
    return operands_buf

def _release_operands_buffer(operands_buf):
    global _free_operands_bufs
    del operands_buf[:]
    _free_operands_bufs.append(operands_buf)

def _expr_create_variadic(solver_ptr, operator, ops):
    if hasattr(ops, "__len__") and len(ops) == 1 and hasattr(ops[0], "__iter__"):
        ops = ops[0]
    operands_buf = _fill_operands_buffer(solver_ptr, ops)
    buf_info = operands_buf.buffer_info()
    expr_id = _ls_create_expression_n(solver_ptr, operator, buf_info[0], buf_info[1])
    _release_operands_buffer(operands_buf)
    return expr_id

def _expr_create_0(solver_ptr, operator):
    return _ls_create_expression(solver_ptr, operator)

def _expr_create_1(solver_ptr, operator, op1):
    rop1 = _autocreate_expr(solver_ptr, op1)
    return _ls_create_expression_1(solver_ptr, operator, rop1)

def _expr_create_2(solver_ptr, operator, op1, op2):
    rop1 = _autocreate_expr(solver_ptr, op1)
    rop2 = _autocreate_expr(solver_ptr, op2)
    return _ls_create_expression_2(solver_ptr, operator, rop1, rop2)

def _expr_create_3(solver_ptr, operator, op1, op2, op3):
    rop1 = _autocreate_expr(solver_ptr, op1)
    rop2 = _autocreate_expr(solver_ptr, op2)
    rop3 = _autocreate_expr(solver_ptr, op3)
    return _ls_create_expression_3(solver_ptr, operator, rop1, rop2, rop3)

def _expr_add_operands(solver_ptr, expr_id, ops):
    if hasattr(ops, "__len__") and len(ops) == 1 and hasattr(ops[0], "__iter__"):
        ops = ops[0]
    operands_buf = _fill_operands_buffer(solver_ptr, ops)
    buf_info = operands_buf.buffer_info()
    _ls_expr_add_operands(solver_ptr, expr_id, buf_info[0], buf_info[1])
    _release_operands_buffer(operands_buf)

def _find_expr_id(solver_ptr, expr):
    if isinstance(expr, LSExpression):
        _check_same_solver(solver_ptr, expr._solver_ptr)
        return expr._expr_id
    elif isinstance(expr, int):
        return expr
    else:
        raise TypeError("An LSExpression or an integer is expected but %s was found" % expr)

def _nb_function_args(callval):
    PYSIG = sys.version_info[0] > 3 or sys.version_info[0] == 3 and sys.version_info[1] >= 3
    if PYSIG:
        signature = inspect.signature(callval)
        return len(signature.parameters)
    else:
        args_def = inspect.getargspec(callval)[0]
        return len(args_def)

def _create_native_function(solver, func_type, func_creator, arg_class, func):
    _check_solver(solver)

    def native_function(ptr, arg_values, userdata):
        try:
            return func(arg_class(solver, arg_values))
        except LSError as e:
            _ls_interrupt(ptr, e.explanation, None)
        except:
            info = sys.exc_info()
            str_ex = _encode_string(repr(info[1]))
            _ls_interrupt(ptr, str_ex, None)
            return 0

    native_func = func_type(native_function)
    solver._native_functions.append(native_func)
    return LSExpression(solver, func_creator(solver._solver_ptr, native_func, None))



########


class LSBlackBoxContext(object):
    __slots__ = "_solver", "_attrs_ptr", "_func_id"

    def __init__(self, solver, func_id):
        self._solver = solver
        self._func_id = func_id
        self._attrs_ptr = _ls_expr_attrs(solver._solver_ptr, func_id)

    def get_lower_bound(self):
        _check_solver(self._solver)
        func_type = _ls_expr_subtype(self._solver._solver_ptr, self._func_id)
        if func_type == _LSVT_INT:
            return _ls_attrs_get_llong(self._attrs_ptr, _encode_string("intLowerBound"))
        elif func_type == _LSVT_DOUBLE:
            return _ls_attrs_get_double(self._attrs_ptr, _encode_string("doubleLowerBound"))
        else:
            raise TypeError("This function does not have a lower bound.")

    def set_lower_bound(self, lower_bound):
        _check_solver(self._solver)
        _ls_check_modeling(self._solver._solver_ptr)
        if isinstance(lower_bound, int):
            _ls_check_expr_subtype(self._solver._solver_ptr, self._func_id, _LSVT_INT)
            _ls_attrs_set_llong(self._attrs_ptr, _encode_string("intLowerBound"), lower_bound)
        else:
            _ls_check_expr_subtype(self._solver._solver_ptr, self._func_id, _LSVT_DOUBLE)
            _ls_attrs_set_double(self._attrs_ptr, _encode_string("doubleLowerBound"), lower_bound)

    def get_upper_bound(self):
        _check_solver(self._solver)
        func_type = _ls_expr_subtype(self._solver._solver_ptr, self._func_id)
        if func_type == _LSVT_INT:
            return _ls_attrs_get_llong(self._attrs_ptr, _encode_string("intUpperBound"))
        elif func_type == _LSVT_DOUBLE:
            return _ls_attrs_get_double(self._attrs_ptr, _encode_string("doubleUpperBound"))
        else:
            raise TypeError("This function does not have an upper bound.")

    def set_upper_bound(self, upper_bound):
        _check_solver(self._solver)
        _ls_check_modeling(self._solver._solver_ptr)
        if isinstance(upper_bound, int):
            _ls_check_expr_subtype(self._solver._solver_ptr, self._func_id, _LSVT_INT)
            _ls_attrs_set_llong(self._attrs_ptr, _encode_string("intUpperBound"), upper_bound)
        else:
            _ls_check_expr_subtype(self._solver._solver_ptr, self._func_id, _LSVT_DOUBLE)
            _ls_attrs_set_double(self._attrs_ptr, _encode_string("doubleUpperBound"), upper_bound)

    def is_nanable(self):
        _check_solver(self._solver)
        _ls_check_expr_subtype(self._solver._solver_ptr, self._func_id, _LSVT_DOUBLE)
        return _ls_attrs_get_bool(self._attrs_ptr, _encode_string("nanable"))

    def set_nanable(self, nanable):
        _check_solver(self._solver)
        _ls_check_modeling(self._solver._solver_ptr)
        _ls_check_expr_subtype(self._solver._solver_ptr, self._func_id, _LSVT_DOUBLE)
        _ls_attrs_set_bool(self._attrs_ptr, _encode_string("nanable"), nanable)

    def get_evaluation_limit(self):
        _check_solver(self._solver)
        return _ls_attrs_get_int(self._attrs_ptr, _encode_string("evaluationLimit"))

    def set_evaluation_limit(self, evaluation_limit):
        _check_solver(self._solver)
        _ls_check_stopped(self._solver._solver_ptr)
        _ls_attrs_set_int(self._attrs_ptr, _encode_string("evaluationLimit"), evaluation_limit)

    lower_bound = property(get_lower_bound, set_lower_bound)
    upper_bound = property(get_upper_bound, set_upper_bound)
    nanable = property(is_nanable, set_nanable)
    evaluation_limit = property(get_evaluation_limit, set_evaluation_limit)

########


class LSParam(object):
    __slots__ = "_solver", "_attrs_ptr", "_writer", "_writer_func"
    
    def __init__(self, solver):
        self._solver = solver
        self._attrs_ptr = _ls_params(solver._solver_ptr)
        self._writer = None
        self._writer_func = None

    def get_time_limit(self):
        _check_solver(self._solver)
        return _ls_attrs_get_int(self._attrs_ptr, _encode_string("timeLimit"))

    def set_time_limit(self, time_limit):
        _check_solver(self._solver)
        _ls_attrs_set_int(self._attrs_ptr, _encode_string("timeLimit"), time_limit)

    def get_iteration_limit(self):
        _check_solver(self._solver)
        return _ls_attrs_get_llong(self._attrs_ptr, _encode_string("iterationLimit"))

    def set_iteration_limit(self, iteration_limit):
        _check_solver(self._solver)
        _ls_attrs_set_llong(self._attrs_ptr, _encode_string("iterationLimit"), iteration_limit)

    def get_seed(self):
        _check_solver(self._solver)
        return _ls_attrs_get_int(self._attrs_ptr, _encode_string("seed"))

    def set_seed(self, seed):
        _check_solver(self._solver)
        _ls_attrs_set_int(self._attrs_ptr, _encode_string("seed"), seed)

    def get_nb_threads(self):
        _check_solver(self._solver)
        return _ls_attrs_get_int(self._attrs_ptr, _encode_string("nbThreads"))

    def set_nb_threads(self, nb_threads):
        _check_solver(self._solver)
        _ls_attrs_set_int(self._attrs_ptr, _encode_string("nbThreads"), nb_threads)

    def get_annealing_level(self):
        _check_solver(self._solver)
        return _ls_attrs_get_int(self._attrs_ptr, _encode_string("annealingLevel"))

    def set_annealing_level(self, annealing_level):
        _check_solver(self._solver)
        _ls_attrs_set_int(self._attrs_ptr, _encode_string("annealingLevel"), annealing_level)

    def get_verbosity(self):
        _check_solver(self._solver)
        return _ls_attrs_get_int(self._attrs_ptr, _encode_string("verbosity"))

    def set_verbosity(self, verbosity):
        _check_solver(self._solver)
        _ls_attrs_set_int(self._attrs_ptr, _encode_string("verbosity"), verbosity)

    def get_time_between_displays(self):
        _check_solver(self._solver)
        return _ls_attrs_get_int(self._attrs_ptr, _encode_string("timeBetweenDisplays"))

    def set_time_between_displays(self, time_between_displays):
        _check_solver(self._solver)
        _ls_attrs_set_int(self._attrs_ptr, _encode_string("timeBetweenDisplays"), time_between_displays)

    def get_time_between_ticks(self):
        _check_solver(self._solver)
        return _ls_attrs_get_int(self._attrs_ptr, _encode_string("timeBetweenTicks"))

    def set_time_between_ticks(self, time_between_ticks):
        _check_solver(self._solver)
        _ls_attrs_set_int(self._attrs_ptr, _encode_string("timeBetweenTicks"), time_between_ticks)

    def get_iteration_between_ticks(self):
        _check_solver(self._solver)
        return _ls_attrs_get_llong(self._attrs_ptr, _encode_string("iterationBetweenTicks"))

    def set_iteration_between_ticks(self, iteration_between_ticks):
        _check_solver(self._solver)
        _ls_attrs_set_llong(self._attrs_ptr, _encode_string("iterationBetweenTicks"), iteration_between_ticks)

    def get_log_file(self):
        _check_solver(self._solver)
        return _read_string(lambda buf, size: _ls_attrs_get_string(self._attrs_ptr, _encode_string("logFile"), buf, size))

    def set_log_file(self, log_file):
        _check_solver(self._solver)
        _ls_attrs_set_string(self._attrs_ptr, _encode_string("logFile"), _encode_string(log_file))

    def get_log_writer(self):
        _check_solver(self._solver)
        return self._writer

    def set_log_writer(self, writer, capabilities = -1):
        _check_solver(self._solver)
        if writer == None:
            _ls_set_log_writer2(self._solver._solver_ptr, None, None, -1)
            self._writer_func = None
            self._writer = None
            return

        if capabilities == -1:
            try:
                capabilities = 1 if writer.isatty() else 0
            except:
                capabilities = 0

        def writer_function(ptr, message, length, _):
            try:
                writer.write(_decode_subset_bytes(message, length))
            except LSError as e:
                _ls_interrupt(ptr, e.explanation, None)
            except:
                info = sys.exc_info()
                str_ex = _encode_string(repr(info[1]))
                _ls_interrupt(ptr, str_ex, None)
                return 0.0

        self._writer_func = _ls_log_writer_type(writer_function)
        self._writer = writer
        _ls_set_log_writer(self._solver._solver_ptr, self._writer_func, None, capabilities)
        
    def get_advanced_param(self, name):
        _check_solver(self._solver)
        if not _ls_attrs_is_defined(self._attrs_ptr, _encode_string(name)): return None
        return _get_attr_value(self._attrs_ptr, name)

    def set_advanced_param(self, name, value):
        _check_solver(self._solver)
        if not _ls_attrs_is_defined(self._attrs_ptr, _encode_string(name)): return
        _set_attr_value(self._attrs_ptr, name, value)

    def get_objective_threshold(self, pos):
        _check_solver(self._solver)
        expr_id = _ls_objective(self._solver._solver_ptr, pos)
        if _ls_expr_type(self._solver._solver_ptr, expr_id) == _LSVT_DOUBLE:
            return _ls_double_objective_threshold(self._solver._solver_ptr, pos)
        else:
            return _ls_int_objective_threshold(self._solver._solver_ptr, pos)

    def set_objective_threshold(self, pos, value):
        _check_solver(self._solver)
        x = _extract_python_number(value)
        if isinstance(x, int):
            _ls_set_int_objective_threshold(self._solver._solver_ptr, pos, x)
        else:
            _ls_set_double_objective_threshold(self._solver._solver_ptr, pos, x)

    def __str__(self):
        _check_solver(self._solver)
        return _read_string(lambda buf, x: _ls_params_to_string(self._attrs_ptr, buf, x))

    def __eq__(self, other):
        return (isinstance(other, LSParam)
            and self._attrs_ptr == other._attrs_ptr)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self._attrs_ptr

    time_limit = property(get_time_limit, set_time_limit)
    iteration_limit = property(get_iteration_limit, set_iteration_limit)
    seed = property(get_seed, set_seed)
    nb_threads = property(get_nb_threads, set_nb_threads)
    verbosity = property(get_verbosity, set_verbosity)
    annealing_level = property(get_annealing_level, set_annealing_level)

    time_between_displays = property(get_time_between_displays, set_time_between_displays)
    time_between_ticks = property(get_time_between_ticks, set_time_between_ticks)
    iteration_between_ticks = property(get_iteration_between_ticks, set_iteration_between_ticks)
    log_file = property(get_log_file, set_log_file)
    log_writer = property(get_log_writer, set_log_writer)
    advanced_params = property(lambda self: LSMutableDict("AdvancedParameter", self.get_advanced_param, self.set_advanced_param))


########


class LSArray(object):
    __slots__ = "_solver", "_buffer_ptr"

    def __init__(self, solver, buffer_ptr):
        self._solver = solver
        self._buffer_ptr = buffer_ptr

    def count(self):
        _check_solver(self._solver)
        return _ls_buffer_count(self._buffer_ptr)

    def is_bool(self, pos):
        _check_solver(self._solver)
        return _ls_buffer_is_bool(self._buffer_ptr, pos)

    def is_int(self, pos):
        _check_solver(self._solver)
        return _ls_buffer_is_int(self._buffer_ptr, pos)

    def is_double(self, pos):
        _check_solver(self._solver)
        return _ls_buffer_is_double(self._buffer_ptr, pos)

    def get(self, pos):
        _check_solver(self._solver)
        buf_type = _ls_buffer_type(self._buffer_ptr, pos)
        if buf_type == _LSVT_INT or buf_type == _LSVT_BOOL:
            return _ls_buffer_get_int(self._buffer_ptr, pos)
        elif buf_type == _LSVT_DOUBLE:
            return _ls_buffer_get_double(self._buffer_ptr, pos)
        elif buf_type == _LSVT_ARRAY:
            return LSArray(self._solver, _ls_buffer_get_buffer(self._buffer_ptr, pos))

    def __getitem__(self, pos):
        return self.get(pos)
    
    def __len__(self):
        return self.count()

    def __iter__(self):
        n = 0
        while (n < self.count()):
            yield self.get(n)
            n += 1

    def __str__(self):
        _check_solver(self._solver)
        return _read_string(lambda buf, x: _ls_buffer_to_string(self._buffer_ptr, buf, x))

    def __hash__(self):
        return self._buffer_ptr

    def __eq__(self, other):
        return (isinstance(other, LSArray)
            and self._buffer_ptr == other._buffer_ptr)

    def __ne__(self, other):
        return not self.__eq__(other)


########


class LSPhase(object):
    __slots__ = "_solver", "_phase_ptr", "_params", "_stats"
    
    def __init__(self, solver, phase_ptr):
        self._solver = solver
        self._phase_ptr = phase_ptr
        self._params = _ls_phase_params(self._phase_ptr)
        self._stats = _ls_phase_stats(self._phase_ptr)

    def get_time_limit(self):
        _check_solver(self._solver)
        return _ls_attrs_get_int(self._params, _encode_string("timeLimit"))

    def set_time_limit(self, limit):
        _check_solver(self._solver)
        _ls_attrs_set_int(self._params, _encode_string("timeLimit"), limit)

    def get_iteration_limit(self):
        _check_solver(self._solver)
        return _ls_attrs_get_llong(self._params, _encode_string("iterationLimit"))

    def set_iteration_limit(self, limit):
        _check_solver(self._solver)
        _ls_attrs_set_llong(self._params, _encode_string("iterationLimit"), limit)

    def get_optimized_objective(self):
        _check_solver(self._solver)
        return _ls_attrs_get_int(self._params, _encode_string("optimizedObjective"))

    def set_optimized_objective(self, pos):
        _check_solver(self._solver)
        _ls_attrs_set_int(self._params, _encode_string("optimizedObjective"), pos)

    def is_enabled(self):
        _check_solver(self._solver)
        return _ls_attrs_get_bool(self._params, _encode_string("enabled"))

    def set_enabled(self, enabled):
        _check_solver(self._solver)
        _ls_attrs_set_bool(self._params, _encode_string("enabled"), enabled)

    def __str__(self):
        _check_solver(self._solver)
        return _read_string(lambda buf, x: _ls_phase_to_string(self._phase_ptr, buf, x))

    def __eq__(self, other):
        return (isinstance(other, LSPhase)
            and self._phase_ptr == other._phase_ptr)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self._phase_ptr

    time_limit = property(get_time_limit, set_time_limit)
    iteration_limit = property(get_iteration_limit, set_iteration_limit)
    optimized_objective = property(get_optimized_objective, set_optimized_objective)
    enabled = property(is_enabled, set_enabled)


########


class LSStatistics(object):
    __slots__ = "_solver", "_attrs_ptr"

    def __init__(self, solver):
        self._solver = solver
        self._attrs_ptr = _ls_stats(solver._solver_ptr)

    def get_running_time(self):
        _check_solver(self._solver)
        return _ls_attrs_get_int(self._attrs_ptr, _encode_string("runningTime"))

    def get_nb_iterations(self):
        _check_solver(self._solver)
        return _ls_attrs_get_llong(self._attrs_ptr, _encode_string("nbIterations"))
        
    def get_nb_moves(self):
        _check_solver(self._solver)
        return _ls_attrs_get_llong(self._attrs_ptr, _encode_string("nbMoves"))
        
    def get_nb_accepted_moves(self):
        _check_solver(self._solver)
        return _ls_attrs_get_llong(self._attrs_ptr, _encode_string("nbAcceptedMoves"))

    def get_nb_improving_moves(self):
        _check_solver(self._solver)
        return _ls_attrs_get_llong(self._attrs_ptr, _encode_string("nbImprovingMoves"))

    def get_nb_infeasible_moves(self):
        _check_solver(self._solver)
        return _ls_attrs_get_llong(self._attrs_ptr, _encode_string("nbInfeasibleMoves"))

    def get_nb_rejected_moves(self):
        _check_solver(self._solver)
        return _ls_attrs_get_llong(self._attrs_ptr, _encode_string("nbRejectedMoves"))

    def get_percent_accepted_moves(self):
        _check_solver(self._solver)
        return _ls_attrs_get_double(self._attrs_ptr, _encode_string("percentAcceptedMoves"))

    def get_percent_improving_moves(self):
        _check_solver(self._solver)
        return _ls_attrs_get_double(self._attrs_ptr, _encode_string("percentImprovingMoves"))

    def get_percent_rejected_moves(self):
        _check_solver(self._solver)
        return _ls_attrs_get_double(self._attrs_ptr, _encode_string("percentRejectedMoves"))

    def get_percent_infeasible_moves(self):
        _check_solver(self._solver)
        return _ls_attrs_get_double(self._attrs_ptr, _encode_string("percentInfeasibleMoves"))

    def __getattr__(self, name):
        _check_solver(self._solver)
        if not _ls_attrs_is_defined(self._attrs_ptr, _encode_string(name)): raise AttributeError
        return _get_attr_value(self._attrs_ptr, name)

    def __getitem__(self, name):
        _check_solver(self._solver)
        if not _ls_attrs_is_defined(self._attrs_ptr, _encode_string(name)): raise KeyError
        return _get_attr_value(self._attrs_ptr, name)

    def __str__(self):
        _check_solver(self._solver)
        return _read_string(lambda buf, x: _ls_attrs_to_string(self._attrs_ptr, buf, x))

    def __eq__(self, other):
        return (isinstance(other, LSStatistics)
            and self._attrs_ptr == other._attrs_ptr)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self._attrs_ptr

    running_time = property(get_running_time)
    nb_iterations = property(get_nb_iterations)
    nb_moves = property(get_nb_moves)
    nb_accepted_moves = property(get_nb_accepted_moves)
    nb_improving_moves = property(get_nb_improving_moves)
    nb_infeasible_moves = property(get_nb_infeasible_moves)
    nb_rejected_moves = property(get_nb_rejected_moves)
    percent_accepted_moves = property(get_percent_accepted_moves)
    percent_improving_moves = property(get_percent_improving_moves)
    percent_rejected_moves = property(get_percent_rejected_moves)
    percent_infeasible_moves = property(get_percent_infeasible_moves)


########


class LSCollection(object):
    __slots__ = "_solver", "_buffer_ptr", "_solution_ptr", "_expr_id"

    def __init__(self, solver, buffer_ptr, solution_ptr = None, expr_id = None):
        self._solver = solver
        self._buffer_ptr = buffer_ptr
        self._solution_ptr = solution_ptr
        self._expr_id = expr_id

    def count(self):
        _check_solver(self._solver)
        return _ls_buffer_count(self._buffer_ptr)

    def get(self, pos):
        _check_solver(self._solver)
        return _ls_buffer_get_int(self._buffer_ptr, pos)

    def contains(self, value):
        _check_solver(self._solver)
        return _ls_buffer_contains_int(self._buffer_ptr, value)

    def add(self, val):
        _check_solver(self._solver)
        _check_readwrite_collection(self._solution_ptr)
        _ls_solution_collection_add(self._solution_ptr, self._expr_id, val);

    def clear(self):
        _check_solver(self._solver)
        _check_readwrite_collection(self._solution_ptr)
        _ls_solution_clear(self._solution_ptr, self._expr_id)

    def __getitem__(self, pos):
        return self.get(pos)
    
    def __len__(self):
        return self.count()

    def __iter__(self):
        n = 0
        while (n < self.count()):
            yield self.get(n)
            n += 1

    def __str__(self):
        _check_solver(self._solver)
        return _read_string(lambda buf, x: _ls_buffer_to_string(self._buffer_ptr, buf, x))

    def __hash__(self):
        return self._buffer_ptr

    def __eq__(self, other):
        return (isinstance(other, LSCollection)
            and self._buffer_ptr == other._buffer_ptr)

    def __ne__(self, other):
        return not self.__eq__(other)

########


class LSVersion(object):
    __slots__ = "_attrs_ptr", 

    def __init__(self):
        self._attrs_ptr = _ls_globals()

    def get_major_version_number(self):
        return _ls_attrs_get_int(self._attrs_ptr, _encode_string("majorVersion"))

    def get_minor_version_number(self):
        return _ls_attrs_get_int(self._attrs_ptr, _encode_string("minorVersion"))

    def get_build_date(self):
        return _ls_attrs_get_int(self._attrs_ptr, _encode_string("buildDate"))

    def get_platform(self):
        return _read_string(lambda buf, size: _ls_attrs_get_string(
                    self._attrs_ptr, _encode_string("platform"), buf, size))

    def get_version(self):
        return _read_string(lambda buf, size: _ls_attrs_get_string(
                    self._attrs_ptr, _encode_string("version"), buf, size))

    def get_version_code(self):
        return _ls_version_code(self._attrs_ptr)

    def get_copyright(self):
        return _read_string(lambda buf, size: _ls_attrs_get_string(
                    self._attrs_ptr, _encode_string("copyright"), buf, size))

    def get_info(self):
        return _read_string(lambda buf, size: _ls_attrs_get_string(
                    self._attrs_ptr, _encode_string("info"), buf, size))

    def get_license_path(self):
        return _read_string(lambda buf, size: _ls_attrs_get_string(
                    self._attrs_ptr, _encode_string("licensePath"), buf, size))

    def set_license_path(self, path):
        _ls_attrs_set_string(self._attrs_ptr, _encode_string("licensePath"), _encode_string(path))

    def get_license_content(self):
        return _read_string(lambda buf, size: _ls_attrs_get_string(
                    self._attrs_ptr, _encode_string("licenseContent"), buf, size))

    def set_license_content(self, content):
        _ls_attrs_set_string(self._attrs_ptr, _encode_string("licenseContent"), _encode_string(content))

    major_version_number = property(get_major_version_number)
    minor_version_number = property(get_minor_version_number)
    build_date = property(get_build_date)
    platform = property(get_platform)
    version = property(get_version)
    version_code = property(get_version_code)
    copyright = property(get_copyright)
    info = property(get_info)
    license_path = property(get_license_path, set_license_path)
    license_content = property(get_license_content, set_license_content)

version = LSVersion()
LSVersion = LSVersion()

########


class LSExternalArgumentValues(object):
    __slots__ = "_solver", "_buffer_ptr"

    def __init__(self, solver, buffer_ptr):
        self._solver = solver
        self._buffer_ptr = buffer_ptr

    def count(self):
        _check_solver(self._solver)
        return _ls_buffer_count(self._buffer_ptr)
    
    def is_bool(self, pos):
        _check_solver(self._solver)
        return _ls_buffer_type(self._buffer_ptr, pos) == _LSVT_BOOL

    def is_int(self, pos):
        _check_solver(self._solver)
        buf_type = _ls_buffer_type(self._buffer_ptr, pos)
        return buf_type == _LSVT_INT or buf_type == _LSVT_BOOL

    def is_double(self, pos):
        _check_solver(self._solver)
        return _ls_buffer_type(self._buffer_ptr, pos) == _LSVT_DOUBLE

    def is_collection(self, pos):
        _check_solver(self._solver)
        return _ls_buffer_type(self._buffer_ptr, pos) == _LSVT_COLLECTION

    def is_array(self, pos):
        _check_solver(self._solver)
        return _ls_buffer_type(self._buffer_ptr, pos) == _LSVT_ARRAY

    def get(self, pos):
        _check_solver(self._solver)
        buf_type = _ls_buffer_type(self._buffer_ptr, pos)
        if buf_type == _LSVT_INT or buf_type == _LSVT_BOOL:
            return _ls_buffer_get_int(self._buffer_ptr, pos)
        elif buf_type == _LSVT_DOUBLE:
            return _ls_buffer_get_double(self._buffer_ptr, pos)
        elif buf_type == _LSVT_COLLECTION:
            return LSCollection(self._solver, _ls_buffer_get_buffer(self._buffer_ptr, pos))
        elif buf_type == _LSVT_ARRAY:
            return LSArray(self._solver, _ls_buffer_get_buffer(self._buffer_ptr, pos))

    def __getitem__(self, pos):
        return self.get(pos)
    
    def __len__(self):
        return self.count()

    def __iter__(self):
        n = 0
        while (n < self.count()):
            yield self.get(n)
            n += 1

    def __str__(self):
        _check_solver(self._solver)
        return _read_string(lambda buf, x: _ls_buffer_to_string(self._buffer_ptr, buf, x))

    def __hash__(self):
        return self._buffer_ptr

    def __eq__(self, other):
        return (isinstance(other, LSExternalArgumentValues)
            and self._buffer_ptr == other._buffer_ptr)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self._buffer_ptr


########


class LSExpression(object):
    __slots__ = "_solver", "_solver_ptr", "_expr_id"

    def __init__(self, solver, expr_id):
        self._solver = solver
        self._solver_ptr = solver._solver_ptr
        self._expr_id = expr_id

    def get_operator(self):
        _check_solver(self._solver)
        return LSOperator[_ls_expr_operator(self._solver_ptr, self._expr_id)]

    def get_index(self):
        _check_solver(self._solver)
        return self._expr_id

    def is_constant(self):
        _check_solver(self._solver)
        return _ls_expr_operator(self._solver_ptr, self._expr_id) == 2

    def is_decision(self):
        _check_solver(self._solver)
        return _ls_expr_is_decision(self._solver_ptr, self._expr_id)

    def is_constraint(self):
        _check_solver(self._solver)
        return _ls_expr_is_constraint(self._solver_ptr, self._expr_id)

    def is_objective(self):
        _check_solver(self._solver)
        return _ls_expr_is_objective(self._solver_ptr, self._expr_id)

    def is_double(self):
        _check_solver(self._solver)
        return _ls_expr_type(self._solver_ptr, self._expr_id) == _LSVT_DOUBLE

    def is_int(self):
        _check_solver(self._solver)
        expr_type = _ls_expr_type(self._solver_ptr, self._expr_id)
        return expr_type == _LSVT_INT or expr_type == _LSVT_BOOL

    def is_bool(self):
        _check_solver(self._solver)
        return _ls_expr_type(self._solver_ptr, self._expr_id) == _LSVT_BOOL

    def is_array(self):
        _check_solver(self._solver)
        return _ls_expr_is_array(self._solver_ptr, self._expr_id) == _LSVT_ARRAY

    def is_collection(self):
        _check_solver(self._solver)
        return _ls_expr_type(self._solver_ptr, self._expr_id) == _LSVT_COLLECTION

    def is_function(self):
        _check_solver(self._solver)
        return _ls_expr_type(self._solver_ptr, self._expr_id) == _LSVT_FUNCTION

    def add_operand(self, operand):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        _ls_expr_add_operand(ptr, self._expr_id, _autocreate_expr(ptr, operand))

    def add_operands(self, operands):
        _check_solver(self._solver)
        _expr_add_operands(self._solver_ptr, self._expr_id, operands)

    def get_nb_operands(self):
        return _ls_expr_nb_operands(self._solver_ptr, self._expr_id)

    def get_operand(self, pos):
        _check_solver(self._solver)
        return LSExpression(self._solver, _ls_expr_operand(self._solver_ptr, self._expr_id, pos))

    def set_operand(self, pos, expr):
        _check_solver(self._solver)
        opId = _autocreate_expr(self._solver_ptr, expr)
        _ls_expr_set_operand(self._solver_ptr, self._expr_id, pos, opId)
    
    def set_value(self, value):
        _check_solver(self._solver)
        x = _extract_python_number(value)
        if isinstance(x, int):
            _ls_solution_set_int_value(_ls_best_solution(self._solver_ptr), self._expr_id, x)
        else:
            _ls_solution_set_double_value(_ls_best_solution(self._solver_ptr), self._expr_id, x)

    def get_value(self):
        _check_solver(self._solver)
        expr_type = _ls_expr_type(self._solver_ptr, self._expr_id)
        solution_ptr = _ls_best_solution(self._solver_ptr)
        if expr_type == _LSVT_INT or expr_type == _LSVT_BOOL:
            return _ls_solution_int_value(solution_ptr, self._expr_id)
        elif expr_type == _LSVT_DOUBLE:
            return _ls_solution_double_value(solution_ptr, self._expr_id)
        elif expr_type == _LSVT_COLLECTION:
            buf = _ls_solution_buffer_value(solution_ptr, self._expr_id)
            return LSCollection(self._solver, buf, solution_ptr, self._expr_id)
        elif expr_type == _LSVT_ARRAY:
            buf = _ls_solution_buffer_value(solution_ptr, self._expr_id)
            return LSArray(self._solver, buf)
        else: 
            raise TypeError("This expression doesn't have any value")

    def get_external_context(self):
        _check_solver(self._solver)
        _ls_check_operator(self._solver_ptr, self._expr_id, 43)
        return LSExternalContext(self._solver, self._expr_id)

    def get_blackbox_context(self):
        _check_solver(self._solver)
        _ls_check_operator(self._solver_ptr, self._expr_id, 50)
        return LSBlackBoxContext(self._solver, self._expr_id)

    def is_violated(self):
        _check_solver(self._solver)
        solution_ptr = _ls_best_solution(self._solver_ptr)
        return _ls_solution_is_violated(solution_ptr, self._expr_id)

    def is_undefined(self):
        _check_solver(self._solver)
        solution_ptr = _ls_best_solution(self._solver_ptr)
        return _ls_solution_is_undefined(solution_ptr, self._expr_id)

    def get_name(self):
        _check_solver(self._solver)
        return _read_string(lambda buf, length: _ls_expr_name(self._solver_ptr, self._expr_id, buf, length))

    def set_name(self, name):
        _check_solver(self._solver)
        _ls_expr_set_name(self._solver_ptr, self._expr_id, _encode_string(name))
    
    def is_named(self):
        _check_solver(self._solver)
        return _ls_expr_name(self._solver_ptr, self._expr_id, None, 0) > 0

    def __str__(self):
        _check_solver(self._solver)
        return _read_string(lambda buf, length: _ls_expr_to_string(self._solver_ptr, self._expr_id, buf, length))

    def __eq__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 8, self._expr_id, _autocreate_expr(ptr, other)))

    def __ne__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 9, self._expr_id, _autocreate_expr(ptr, other)))

    def __ge__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 10, self._expr_id, _autocreate_expr(ptr, other)))

    def __le__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 11, self._expr_id, _autocreate_expr(ptr, other)))

    def __gt__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 12, self._expr_id, _autocreate_expr(ptr, other)))

    def __lt__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 13, self._expr_id, _autocreate_expr(ptr, other)))

    def __and__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 16, self._expr_id, _autocreate_expr(ptr, other)))

    def __rand__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 16, _autocreate_expr(ptr, other), self._expr_id))

    def __or__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 17, self._expr_id, _autocreate_expr(ptr, other)))

    def __ror__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 17, _autocreate_expr(ptr, other), self._expr_id))

    def __xor__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 18, self._expr_id, _autocreate_expr(ptr, other)))

    def __rxor__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 18, _autocreate_expr(ptr, other), self._expr_id))

    def __invert__(self):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_1(self._solver_ptr, 15, self))

    def __add__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 3, self._expr_id, _autocreate_expr(ptr, other)))

    def __radd__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 3, _autocreate_expr(ptr, other), self._expr_id))

    def __sub__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 4, self._expr_id, _autocreate_expr(ptr, other)))

    def __rsub__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 4, _autocreate_expr(ptr, other), self._expr_id))

    def __mul__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 5, self._expr_id, _autocreate_expr(ptr, other)))

    def __rmul__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 5, _autocreate_expr(ptr, other), self._expr_id))

    def __div__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 21, self._expr_id, _autocreate_expr(ptr, other)))

    def __rdiv__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 21, _autocreate_expr(ptr, other), self._expr_id))

    def __truediv__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 21, self._expr_id, _autocreate_expr(ptr, other)))

    def __rtruediv__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 21, _autocreate_expr(ptr, other), self._expr_id))

    def __floordiv__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_1(ptr, 27, 
                _ls_create_expression_2(ptr, 21, self._expr_id, _autocreate_expr(ptr, other))))

    def __rfloordiv__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_1(ptr, 27, 
                _ls_create_expression_2(ptr, 21, _autocreate_expr(ptr, other), self._expr_id)))

    def __pow__(self, other, z = 1):
        if (not z is None) and z != 1:
            raise ValueError("Modulo on pow is not supported")
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 32, self._expr_id, _autocreate_expr(ptr, other)))

    def __rpow__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 32, _autocreate_expr(ptr, other), self._expr_id))

    def __mod__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 22, self._expr_id, _autocreate_expr(ptr, other)))

    def __rmod__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 22, _autocreate_expr(ptr, other), self._expr_id))

    def __neg__(self):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 4, _ls_create_int_constant(ptr, 0), self._expr_id))

    def __pos__(self):
        _check_solver(self._solver)
        return self

    def __abs__(self):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_1(ptr, 19, self._expr_id))

    def __getitem__(self, other):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        return LSExpression(self._solver, _ls_create_expression_2(ptr, 24, self._expr_id, _autocreate_expr(ptr, other)))

    def __call__(self, *args):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        expr = _ls_create_expression_1(ptr, 44, self._expr_id)
        _expr_add_operands(ptr, expr, args)
        return LSExpression(self._solver, expr)

    def __hash__(self):
        return self._solver_ptr + self._expr_id*7

    operator = property(get_operator)
    index = property(get_index)
    nb_operands = property(get_nb_operands)
    operands = property(lambda self: LSMutableContainer("LSExpression", self.get_nb_operands, self.get_operand, self.set_operand))
    name = property(get_name, set_name)
    value = property(get_value, set_value)
    blackbox_context = property(get_blackbox_context)
    external_context = property(get_external_context)

########


class LSBlackBoxArgumentValues(object):
    __slots__ = "_solver", "_buffer_ptr"

    def __init__(self, solver, buffer_ptr):
        self._solver = solver
        self._buffer_ptr = buffer_ptr

    def count(self):
        _check_solver(self._solver)
        return _ls_buffer_count(self._buffer_ptr)
    
    def is_bool(self, pos):
        _check_solver(self._solver)
        return _ls_buffer_type(self._buffer_ptr, pos) == _LSVT_BOOL

    def is_int(self, pos):
        _check_solver(self._solver)
        buf_type = _ls_buffer_type(self._buffer_ptr, pos)
        return buf_type == _LSVT_INT or buf_type == _LSVT_BOOL

    def is_double(self, pos):
        _check_solver(self._solver)
        return _ls_buffer_type(self._buffer_ptr, pos) == _LSVT_DOUBLE

    def get(self, pos):
        _check_solver(self._solver)
        buf_type = _ls_buffer_type(self._buffer_ptr, pos)
        if buf_type == _LSVT_INT or buf_type == _LSVT_BOOL:
            return _ls_buffer_get_int(self._buffer_ptr, pos)
        elif buf_type == _LSVT_DOUBLE:
            return _ls_buffer_get_double(self._buffer_ptr, pos)

    def __getitem__(self, pos):
        return self.get(pos)
    
    def __len__(self):
        return self.count()

    def __iter__(self):
        n = 0
        while (n < self.count()):
            yield self.get(n)
            n += 1

    def __str__(self):
        _check_solver(self._solver)
        return _read_string(lambda buf, x: _ls_buffer_to_string(self._buffer_ptr, buf, x))

    def __hash__(self):
        return self._buffer_ptr

    def __eq__(self, other):
        return (isinstance(other, LSBlackBoxArgumentValues)
            and self._buffer_ptr == other._buffer_ptr)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self._buffer_ptr


########


class LSModel(object):
    __slots__ = "_solver", "_solver_ptr"

    def __init__(self, solver):
        self._solver = solver
        self._solver_ptr = solver._solver_ptr

    def close(self):
        _check_solver(self._solver)
        _ls_close(self._solver_ptr)

    def open(self):
        _check_solver(self._solver)
        _ls_open(self._solver_ptr)

    def is_closed(self):
        _check_solver(self._solver)
        return _ls_is_closed(self._solver_ptr)

    def create_constant(self, constant):
        _check_solver(self._solver)
        x = _extract_python_number(constant)
        if isinstance(x, int):
            return LSExpression(self._solver, _ls_create_int_constant(self._solver_ptr, x))
        else:
            return LSExpression(self._solver, _ls_create_double_constant(self._solver_ptr, x))

    def create_lambda_function(self, functor):
        _check_solver(self._solver)
        if not inspect.isfunction(functor):
            raise TypeError("A function is expected but " + repr(functor) + " was found")

        nb_args = _nb_function_args(functor)
        arguments = [LSExpression(self._solver, _expr_create_0(self._solver_ptr, 46)) for i in range(nb_args)]
        arguments.append(functor(*arguments))
        return LSExpression(self._solver, _expr_create_variadic(self._solver_ptr, 45, arguments))

    def create_int_external_function(self, func):
        return _create_native_function(self._solver, _ls_int_native_function_type, 
                _ls_create_int_external_function, LSExternalArgumentValues, func)

    def create_double_external_function(self, func):
        return _create_native_function(self._solver, _ls_double_native_function_type, 
                _ls_create_double_external_function, LSExternalArgumentValues, func)

    def create_double_blackbox_function(self, func):
        return _create_native_function(self._solver, _ls_double_native_function_type,
                _ls_create_double_blackbox_function, LSBlackBoxArgumentValues, func)

    def add_objective(self, expr, direction):
        _check_solver(self._solver)
        _check_enum(direction, LSObjectiveDirection)
        _ls_add_objective(self._solver_ptr, _autocreate_expr(self._solver_ptr, expr), direction.value)

    def minimize(self, expr):
        _check_solver(self._solver)
        self.add_objective(expr, LSObjectiveDirection.MINIMIZE)

    def maximize(self, expr):
        _check_solver(self._solver)
        self.add_objective(expr, LSObjectiveDirection.MAXIMIZE)

    def get_nb_objectives(self):
        _check_solver(self._solver)
        return _ls_nb_objectives(self._solver_ptr)

    def remove_objective(self, pos):
        _check_solver(self._solver)
        _ls_remove_objective(self._solver_ptr, pos)

    def get_expression(self, posOrName):
        _check_solver(self._solver)
        if _is_string(posOrName):
            return LSExpression(self._solver, _ls_expression_with_name(self._solver_ptr, _encode_string(posOrName)))
        else:
            _ls_check_expr_index(self._solver_ptr, posOrName);
            return LSExpression(self._solver, posOrName)

    def get_nb_expressions(self):
        _check_solver(self._solver)
        return _ls_nb_expressions(self._solver_ptr)

    def get_objective(self, pos):
        _check_solver(self._solver)
        return LSExpression(self._solver, _ls_objective(self._solver_ptr, pos))

    def get_objective_direction(self, pos):
        _check_solver(self._solver)
        return LSObjectiveDirection[_ls_objective_direction(self._solver_ptr, pos)]

    def get_nb_constraints(self):
        _check_solver(self._solver)
        return _ls_nb_constraints(self._solver_ptr)

    def remove_constraint(self, expr):
        _check_solver(self._solver)
        if isinstance(expr, int):
            _ls_remove_constraint(self._solver_ptr, expr)
        else:
            _ls_remove_constraint_with_expr(self._solver_ptr, _find_expr_id(self._solver_ptr, expr))

    def get_constraint(self, pos):
        _check_solver(self._solver)
        return LSExpression(self._solver, _ls_constraint(self._solver_ptr, pos))
    
    def add_constraint(self, expr):
        _check_solver(self._solver)
        _ls_add_constraint(self._solver_ptr, _autocreate_expr(self._solver_ptr, expr))

    def constraint(self, expr):
        _check_solver(self._solver)
        self.add_constraint(expr)

    def get_nb_decisions(self):
        _check_solver(self._solver)
        return _ls_nb_decisions(self._solver_ptr)

    def get_decision(self, pos):
        _check_solver(self._solver)
        return LSExpression(self._solver, _ls_decision(self._solver_ptr, pos))

    def get_nb_operands(self):
        _check_solver(self._solver)
        return _ls_nb_operands(self._solver_ptr)

    def create_expression(self, operator, *args):
        _check_solver(self._solver)
        _check_enum(operator, LSOperator)
        return LSExpression(self._solver, _expr_create_variadic(self._solver_ptr, operator.value, args))

    def bool(self):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_0(self._solver_ptr, 0))

    def float(self, arg1, arg2):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 1, arg1, arg2))

    def sum(self, *args):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_variadic(self._solver_ptr, 3, args))

    def sub(self, arg1, arg2):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 4, arg1, arg2))

    def prod(self, *args):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_variadic(self._solver_ptr, 5, args))

    def max(self, *args):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_variadic(self._solver_ptr, 6, args))

    def min(self, *args):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_variadic(self._solver_ptr, 7, args))

    def eq(self, arg1, arg2):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 8, arg1, arg2))

    def neq(self, arg1, arg2):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 9, arg1, arg2))

    def geq(self, arg1, arg2):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 10, arg1, arg2))

    def leq(self, arg1, arg2):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 11, arg1, arg2))

    def gt(self, arg1, arg2):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 12, arg1, arg2))

    def lt(self, arg1, arg2):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 13, arg1, arg2))

    def iif(self, arg1, arg2, arg3):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_3(self._solver_ptr, 14, arg1, arg2, arg3))

    def not_(self, arg1):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_1(self._solver_ptr, 15, arg1))

    def and_(self, *args):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_variadic(self._solver_ptr, 16, args))

    def or_(self, *args):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_variadic(self._solver_ptr, 17, args))

    def xor(self, *args):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_variadic(self._solver_ptr, 18, args))

    def abs(self, arg1):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_1(self._solver_ptr, 19, arg1))

    def dist(self, arg1, arg2):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 20, arg1, arg2))

    def div(self, arg1, arg2):
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 21, arg1, arg2))

    def mod(self, arg1, arg2):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 22, arg1, arg2))

    def array(self, ops = None, opFunc = None):
        _check_solver(self._solver)
        ptr = self._solver_ptr
        expr_id = _expr_create_0(ptr, 23)

        if ops is None:
            ops = []
        if not opFunc is None:
            return LSExpression(self._solver, _expr_create_variadic(ptr, 23, [ops, opFunc]))

        for op in ops:
            if not hasattr(op, "__iter__"):
                _ls_expr_add_operand(ptr, expr_id, _autocreate_expr(ptr, op))
            else:
                subArray = self.array(op)
                _ls_expr_add_operand(ptr, expr_id, subArray._expr_id)

        return LSExpression(self._solver, expr_id)

    def at(self, arg1, *args):
        _check_solver(self._solver)
        concat_args = [arg1]
        concat_args.extend(args)
        return LSExpression(self._solver, _expr_create_variadic(self._solver_ptr, 24, concat_args))

    def scalar(self, arg1, arg2):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 25, arg1, arg2))

    def ceil(self, arg1):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_1(self._solver_ptr, 26, arg1))

    def floor(self, arg1):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_1(self._solver_ptr, 27, arg1))

    def round(self, arg1):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_1(self._solver_ptr, 28, arg1))

    def sqrt(self, arg1):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_1(self._solver_ptr, 29, arg1))

    def log(self, arg1):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_1(self._solver_ptr, 30, arg1))

    def exp(self, arg1):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_1(self._solver_ptr, 31, arg1))

    def pow(self, arg1, arg2):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 32, arg1, arg2))

    def cos(self, arg1):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_1(self._solver_ptr, 33, arg1))

    def sin(self, arg1):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_1(self._solver_ptr, 34, arg1))

    def tan(self, arg1):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_1(self._solver_ptr, 35, arg1))

    def int(self, arg1, arg2):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 36, arg1, arg2))

    def piecewise(self, arg1, arg2, arg3):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_3(self._solver_ptr, 37, arg1, arg2, arg3))

    def list(self, arg1):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_1(self._solver_ptr, 38, arg1))

    def count(self, arg1):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_1(self._solver_ptr, 39, arg1))

    def index(self, arg1, arg2):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 40, arg1, arg2))

    def partition(self, *args):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_variadic(self._solver_ptr, 41, args))

    def disjoint(self, *args):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_variadic(self._solver_ptr, 42, args))

    def call(self, *args):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_variadic(self._solver_ptr, 44, args))

    def range(self, arg1, arg2=None):
        _check_solver(self._solver)
        range_b = 0 if arg2 is None else arg1
        range_e = arg1 if arg2 is None else arg2
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 47, range_b, range_e))

    def int_external_function(self, func):
        _check_solver(self._solver)
        return self.create_int_external_function(func)

    def double_external_function(self, func):
        _check_solver(self._solver)
        return self.create_double_external_function(func)

    def double_blackbox_function(self, func):
        _check_solver(self._solver)
        return self.create_double_blackbox_function(func)
    
    def lambda_function(self, func):
        _check_solver(self._solver)
        return self.create_lambda_function(func)

    def contains(self, arg1, arg2):
        return LSExpression(self._solver, _expr_create_2(self._solver_ptr, 48, arg1, arg2))

    def set(self, arg1):
        _check_solver(self._solver)
        return LSExpression(self._solver, _expr_create_1(self._solver_ptr, 49, arg1))

    def __str__(self):
        _check_solver(self._solver)
        return _read_string(lambda buf, length: _ls_model_to_string(self._solver_ptr, buf, length))

    def __eq__(self, other):
        return (isinstance(other, LSModel)
            and self._solver_ptr == other._solver_ptr)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self._solver_ptr

    nb_objectives = property(get_nb_objectives)
    nb_operands = property(get_nb_operands)
    nb_expressions = property(get_nb_expressions)
    nb_constraints = property(get_nb_constraints)
    nb_decisions = property(get_nb_decisions)
    decisions = property(lambda self: LSContainer("LSExpression", self.get_nb_decisions, self.get_decision))
    expressions = property(lambda self: LSContainer("LSExpression", self.get_nb_expressions, self.get_expression))
    constraints = property(lambda self: LSContainer("LSExpression", self.get_nb_constraints, self.get_constraint))
    objectives = property(lambda self: LSContainer("LSExpression", self.get_nb_objectives, self.get_objective))
    objective_directions = property(lambda self: LSContainer("LSExpression", self.get_nb_objectives, self.get_objective_direction))


########


class LSInconsistency(object):
    __slots__ = "_solver", "_solver_ptr"

    def __init__(self, solver):
        self._solver = solver
        self._solver_ptr = solver._solver_ptr

    def get_nb_causes(self):
        _check_solver(self._solver)
        return _ls_iis_nb_causes(self._solver_ptr)

    def get_cause(self, causeIndex):
        _check_solver(self._solver)
        return LSExpression(self._solver, _ls_iis_cause(self._solver_ptr, causeIndex))

    def __str__(self):
        _check_solver(self._solver)
        return _read_string(lambda buf, x: _ls_iis_to_string(self._solver_ptr, buf, x))

    def __eq__(self, other):
        return (isinstance(other, LSInconsistency)
            and self._solver_ptr == other._solver_ptr)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self._solver_ptr

    def __len__(self):
        return self.get_nb_causes()

    def __getitem__(self, pos):
        return self.get_cause(pos)

########


class LSSolution(object):
    __slots__ = "_solver", "_solver_ptr", "_solution_ptr"
    
    def __init__(self, solver, solution_ptr):
        self._solver = solver
        self._solver_ptr = solver._solver_ptr
        self._solution_ptr = solution_ptr

    def get_value(self, expr):
        _check_solver(self._solver)
        if not isinstance(expr, LSExpression):
            raise TypeError("An LSExpression is expected but " + repr(expr) + " was found")
        _check_same_solver(self._solver_ptr, expr._solver_ptr)

        expr_type = _ls_expr_type(self._solver_ptr, expr._expr_id)
        if expr_type == _LSVT_INT or expr_type == _LSVT_BOOL:
            return _ls_solution_int_value(self._solution_ptr, expr._expr_id)
        elif expr_type == _LSVT_DOUBLE:
            return _ls_solution_double_value(self._solution_ptr, expr._expr_id)
        elif expr_type == _LSVT_COLLECTION:
            buf = _ls_solution_buffer_value(self._solution_ptr, expr._expr_id)
            return LSCollection(self._solver, buf, self._solution_ptr, expr._expr_id)
        elif expr_type == _LSVT_ARRAY:
            return LSArray(self._solver, _ls_solution_buffer_value(self._solution_ptr, expr._expr_id))
        else: 
            raise TypeError("This expression doesn't have any value")
            
    def get_objective_bound(self, pos):
        _check_solver(self._solver)
        expr_id = _ls_objective(self._solver_ptr, pos)
        expr_type = _ls_expr_type(self._solver_ptr, expr_id)
        if expr_type == _LSVT_INT or expr_type == _LSVT_BOOL:
            return _ls_solution_int_objective_bound(self._solution_ptr, pos)
        else:
            return _ls_solution_double_objective_bound(self._solution_ptr, pos)

    def set_value(self, expr, value):
        _check_solver(self._solver)
        if not isinstance(expr, LSExpression):
            raise TypeError("An LSExpression is expected but " + repr(expr) + " was found")
        _check_same_solver(self._solver_ptr, expr._solver_ptr)

        x = _extract_python_number(value)
        if isinstance(x, int):
            _ls_solution_set_int_value(self._solution_ptr, expr._expr_id, x)
        else:
            _ls_solution_set_double_value(self._solution_ptr, expr._expr_id, x)

    def is_violated(self, expr):
        _check_solver(self._solver)

        if not isinstance(expr, LSExpression):
            raise TypeError("An LSExpression is expected but " + repr(expr) + " was found")

        _check_same_solver(self._solver_ptr, expr._solver_ptr)
        return _ls_solution_is_violated(self._solution_ptr, expr._expr_id)

    def is_undefined(self, expr):
        _check_solver(self._solver)

        if not isinstance(expr, LSExpression):
            raise TypeError("An LSExpression is expected but " + repr(expr) + " was found")

        _check_same_solver(self._solver_ptr, expr._solver_ptr)
        return _ls_solution_is_undefined(self._solution_ptr, expr._expr_id)

    def get_status(self):
        _check_solver(self._solver)
        return LSSolutionStatus[_ls_solution_status(self._solution_ptr)]

    def clear(self):
        _check_solver(self._solver)
        _ls_solution_clear(self._solution_ptr)

    def __eq__(self, other):
        return (isinstance(other, LSSolution)
            and self._solution_ptr == other._solution_ptr)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self._solution_ptr

    status = property(get_status)


########


class LocalSolver(object):
    __slots__ = "_solver_ptr", "_callbacks", "_native_functions", "_model", "_stats", "_param", "_solution"

    def __init__(self):
        self._solver_ptr = _ls_create_solver()
        self._callbacks = []
        self._native_functions = []
        self._model = None
        self._stats = None
        self._param = None
        self._solution = None
        self.add_callback(LSCallbackType.TIME_TICKED, lambda ls, type: None)
        self.add_callback(LSCallbackType.DISPLAY, lambda ls, type: None)
        self._configure_log_writer()

    def __del__(self):
        self.delete()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.delete()

    def delete(self):
        if self._solver_ptr != None:
            _ls_delete_solver(self._solver_ptr)
            self._solver_ptr = None
    
    def get_state(self):
        _check_solver(self)
        return LSState[_ls_state(self._solver_ptr)]

    def get_model(self):
        _check_solver(self)
        if self._model != None: return self._model
        self._model = LSModel(self)
        return self._model

    def get_param(self):
        _check_solver(self)
        if self._param != None: return self._param
        self._param = LSParam(self)
        return self._param

    def solve(self):
        _check_solver(self)
        try:
            _ls_define_signal_handler("SIGINT")
            _solvers_stack.append(self)
            _ls_solve(self._solver_ptr)
            _solvers_stack.pop()
        except:
            _solvers_stack.pop()
            raise

    def compute_inconsistency(self):
        _check_solver(self)
        _ls_compute_iis(self._solver_ptr)
        return LSInconsistency(self)

    def stop(self):
        _check_solver(self)
        _ls_stop(self._solver_ptr)

    def create_phase(self):
        _check_solver(self)
        return LSPhase(self, _ls_add_phase(self._solver_ptr))

    def get_phase(self, pos):
        _check_solver(self)
        return LSPhase(self, _ls_phase(self._solver_ptr, pos))

    def get_nb_phases(self):
        _check_solver(self)
        return _ls_nb_phases(self._solver_ptr)

    def get_solution(self):
        _check_solver(self)
        if self._solution != None: return self._solution
        self._solution = LSSolution(self, _ls_best_solution(self._solver_ptr))
        return self._solution

    def get_statistics(self):
        _check_solver(self)
        if self._stats != None: return self._stats
        self._stats = LSStatistics(self)
        return self._stats

    def save_environment(self, filename):
        _check_solver(self)
        _ls_save_environment(self._solver_ptr, _encode_string(filename))

    def load_environment(self, filename):
        _check_solver(self)
        _ls_load_environment(self._solver_ptr, _encode_string(filename))

    def __str__(self):
        _check_solver(self)
        return _read_string(lambda buf, length: _ls_to_string(self._solver_ptr, buf, length))


    def add_callback(self, type, func):
        _check_solver(self)
        _check_enum(type, LSCallbackType)

        def callback(ptr, type, userdata):
            global _pending_error
            try:
                func(self, LSCallbackType[type])
            except:
                _pending_error = sys.exc_info()[1]
                _ls_interrupt(ptr, _encode_string(repr(_pending_error)), ptr)

        cb = (self, func, type, _ls_callback_type(callback))
        self._callbacks.append(cb)
        _ls_add_callback(self._solver_ptr, type.value, cb[3], None)

    def remove_callback(self, type, func):
        _check_solver(self)
        for cb in self._callbacks:
            if cb[1] == func and cb[2] == type:
                return _ls_remove_callback(self._solver_ptr, type.value, cb[3])
        self._callbacks = [cb for cb in self._callbacks if not(cb[1] == func and cb[2] == type)]

    def _configure_log_writer(self):
        try:
            get_ipython()
            self.param.set_log_writer(sys.stdout, 2)
            self.param.advanced_params['nbDisplayedObjs'] = 5
        except:
            if sys.stdout != sys.__stdout__ and sys.stdout != None:
                self.param.set_log_writer(sys.stdout)

    def __eq__(self, other):
        return (isinstance(other, LocalSolver)
            and self._solver_ptr == other._solver_ptr)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self._solver_ptr

    state = property(get_state)
    statistics = property(get_statistics)
    model = property(get_model)
    param = property(get_param)
    solution = property(get_solution)
    nb_phases = property(get_nb_phases)
    phases = property(lambda self: LSContainer("LSPhase", self.get_nb_phases, self.get_phase))



########

