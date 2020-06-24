import multiprocessing

def myfunc(a,b):
    print(a+b)
	mgr = multiprocessing.Manager()
    return a+b