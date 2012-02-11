from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse


def index(request):
	return render_to_response('polls/index.html', )


def gen_phrases(request):
    """
        if request.is_ajax():

            prIds = request.POST.getlist("id")
            if len(prIds) == 0:
                return HttpResponse(" id-Array length = 0 ")

            words = {}
            for id in prIds:
                words[int(id)] = [
                                    request.POST.get("category"+str(id), ""),
                                    request.POST.get("typePrefix"+str(id), ""),
                                    request.POST.get("vendor"+str(id), ""),
                                    request.POST.get("model"+str(id), "")
                                ]
            #wsnum = wordstat_report(k_subsets(words[int(prIds[0])],2))

            #return HttpResponse(str(wsnum))
        else:
            return HttpResponse("Security error")

    #def check_phrases(request):

        #return HttpResponse(check_wordstat_report())

    #def get_phrases(request):

        #return HttpResponse(get_wordstat_report(359469)())
    """

	
	
def k_factorial(ind, words, k):
	
	if ind == k:
		return [ w for w in words ]
	
	else:
		
		arr = []
		for w in words:
			for w1 in k_factorial(ind+1, [s for s in words if s != w ], k):
				arr.append(w+" "+w1)
			
		return arr
	
def k_set_factorial(ind, words, k):
	
	if ind == k-1:
		return [ w for w in words ]
	
	else:
		
		arr = []
		i = 1
		for w in words:
			if i < len(words):
				for w1 in k_set_factorial(ind+1, words[i:], k):
					arr.append(w+" "+w1)
			else: 
				arr.append(w)
			
			i = i + 1
		return arr
	
	
def k_subsets(words, k):
	
	if k > len(words):
		return False
	
	phrases = k_set_factorial(0, words, k)
	
	return phrases 



#print k_subsets(['1','2','3','4'], 3)


	
	
	
	



