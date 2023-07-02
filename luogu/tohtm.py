from markdown import markdown
head='''<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <script type="text/javascript" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML"></script>
    <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
	    tex2jax: {
	        inlineMath: [['$','$'], ['\\(','\\)']],
	        processEscapes: true
	    }
	});
    </script>
</head>'''
for i in range(1002,4001):
    print(i)
    try:
        fname='P'+str(i)
        f = open(fname+'.html','r+',encoding='utf-8')
        old=f.read()
        f.seek(0)
        f.write(head)
        f.write(old)
        f.close()
    except Exception:
        pass



