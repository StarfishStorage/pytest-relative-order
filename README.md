# pytest-relative-order
a pytest plugin that sorts tests using "before" and "after" markers

# Highlights
Consider `file.py`:
```
import pytest

@pytest.mark.after('test3')
def test1():
    pass

@pytest.mark.before('test3')
def test2():
    pass

def test3():
    pass
```

then if you run `pytest file.py`, you should get tests executed in the following order:
```
==================================== test session starts ====================================
platform linux -- Python 3.7.9
cachedir: .pytest_cache
rootdir: /home/radek/example, configfile: pytest.ini
plugins: relative-order-0.2
collected 3 items                                                                                                                                                                                        

file.py::test2 PASSED                                                                  [  33%]
file.py::test3 PASSED                                                                  [  33%]
file.py::test1 PASSED                                                                  [  33%]
===================================== 3 passed in 0.02s =====================================
```

# Details
This plugin introduces two custom markers - `before` and `after`. They accept id of test that should precede/follow the marked test. 
Marker values are used to sort tests with Kahn's algorithm.
## Markers usage
The following usages are correct:
```
@pytest.mark.before('test2')
def test1():
```
```
class TestClass:
  @pytest.mark.before('TestClass::test2')
  def test1():
```
```
class TestClass:
  @pytest.mark.before('filepath.py::TestClass::test2')
  def test1():
```
```
@pytest.mark.after('test2', 'test3', 'test4')
def test1():
```
Marker values must be unique, so if there are two different tests named `test_simple`, but they are in two different classes, then class name must be included in the marker value:
```
class TestClass1:
  def test_simple():
[...]
class TestClass2:
  def test_simple():
[...]

@pytest.mark.after('test_simple')  # wrong, ambiguous!
def test_complex1():
[...]

@pytest.mark.after('TestClass2::test_simple')  # correct
def test_complex2():
[...]
```

Of course cycles are forbidden:
```
@pytest.mark.after('test2')
def test1():
[...]
@pytest.mark.after('test1')  # wrong!
def test2():
[...]
```

## Remarks
Please keep in mind that the configuration below:

`file1.py`:
```
def test1():
  pass
```
`file2.py`:
```
import pytest

pytest.mark.before('file1.py::test1')
def test2():
  pass
```

followed by `pytest file1.py` will NOT detect `test2` and will not execute it.
