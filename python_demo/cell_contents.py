class X: ...

def f():
    f() # what happens here?
    # f is not bound in this scope, it must look to a higher scope to find it.
    # there are two cases:
    #   * the next scope is the global scope
    #   * the next scope is NOT the global scope

def g():
    print("global g")
    def g(next=True):
        print("inner g")
        if next: g()
    return g
