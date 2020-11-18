import json
import sys
import os
filename = sys.argv[1]
key = []
js = filename+'.txt'
inp = filename+'.py'
out = filename+'_asm.txt'
ts = sys.argv[2]+'/typedict.txt'

# input Control Flow Graphs is stored in json formate
with open(js) as jfile: 
	data=json.load(jfile)
	key= sorted(data.keys())
     
#Store data code lines
lines = []		
with open(inp,'r') as fp:
	for line in fp:
		lines.append(line.strip())

n=len(lines)
typeDict = {}

#Open Data type dictionary if it exists
if os.path.exists(ts):
	with open(ts) as tfile:
		typeDict=json.load(tfile)		

popList = []		# List for the items need to remove
assigncall = {} 	# Data assignment through function calls
funpara = {}		# Data assignments in function definitions
nonParaData = {}

#Evaluate the data type of API Call Arguments
def typeBracel(word):
	
	w1 = word.find('(')
	wpara = word[:w1].strip()
	#Evaluate data type from function definition such def function(para1=INT,para2=STRING)
	if wpara in funpara: 
		para = word[w1+1:-1].strip().split(',')
		i=0
		for p in para:
			if p in typeDict:
				l = funpara[str(wpara)][i]
				typeDict[str(l)] = typeDict[str(p)]
			i+=1
		
	#Evaluate data type of arguments		
	res = ''
	if w1>=0: 
		
		#type present in dictionary
		if str(word[:w1].strip()) in typeDict:
			res += typeDict[str(word[:w1].strip())] + '('
		else:
			res += word[:w1].strip()+'('
		w2 = word[w1+1:-1]
		p1 = w2.find('(')
		p2 = w2.find(',')
		if p1>p2 or p1<0:
			word = w2.strip().split(',')
			
			#processing on list of arguments
			for w in word:
				w=w.strip()
				if w!='':
					if w in typeDict:
						
						res += typeDict[w]+','
					else:
						if w.count('=')>0:
							res += equation(w)+','
						else:
							res += rightType(w)+','
			if res.count(',')>0:
				res = res[:-1]
			
		else:
			res += typeBracel(w2)
		
		if res.count('(') > res.count(')'):
			res +=')'
	else:
		res +=word
	
	return res


#Evaluate the type of right hand side data of an equation
def rightType(right):
	
	ret=''
	pb = right.find('(')
	#if predefined input funtion
	if right.find('input(')==0:
		ret = 'String'	
	#if present in dictionary of types
	elif right in typeDict:
		ret = typeDict[right]
	#Boolean data type
	elif right == 'False' or right == 'True':
		ret = 'Boolean'
	#List data type
	elif right.find('[')>=0 and (pb == -1 or right.find('[') <= pb):
		ret = 'List'
	#String data type
	elif (right.find("'")>=0 and (pb == -1 or right.find("'")<=pb)) or (right.find('"')>=0 and (pb == -1 or right.find('"')<=pb)):
		ret = 'String'
	#Dictionary data type
	elif right.find('dict(')>=0 and (pb == -1 or right.find('dict(') <= pb):
		ret = 'Dict'
	#Tuple data type
	elif right.find('tuple(')>=0 and (pb == -1 or right.find('tuple(') <= pb):
		ret = 'Tuple'
	#List type
	elif right.find('list(')>=0 and (pb == -1 or right.find('list(') <= pb):
		ret = 'List'
	#Return type of function call
	elif right.find('(')>=0 or right.find('.')>=0: 
		dotright = right.split('.')
		flag = '.'
		for rd in dotright:
			if rd.count('(')!=rd.count(')'):
				flag = '('
				break
		
		if right.count('.')>0 and (flag=='.' or (right.find('.')<right.find('('))):
			
			#listing arguments and calls used using '.' operator 
			dotlist = []
			if flag == '.':
				dotlist = dotright
			else:
				pr1 = right.find('.')
				while pr1>=0:
					bloc = right[:pr1]
					if bloc.count('(')==bloc.count(')'):
						dotlist.append(bloc)
						right = right[pr1+1:]
						pr1 = right.find('.')
						
					else:
						pr1 = right.find('.',pr1+1)
				dotlist.append(right)
			res=''
			
			#findinf type value of each entity joine by '.'
			for word in dotlist:
					
				if word in typeDict:
					res += typeDict[word]+'.'
				else:
					res += typeBracel(word)+'.'
				
			if res[-1]=='.':
				res = res[:-1]	
			ret = res

		else:
			
			ret = typeBracel(right)
		
		#data[str(num)]['label'] = ret
	#Float type
	elif right.find('/')>=0:
		ret = 'Float'
	#Integer Type
	elif right.find('*')>=0:
		ret = 'Int'
	#Can be float or integer using ASCII value of single char
	elif ord(right.strip()[0])>=48 and ord(right.strip()[0])<=57:
		if right.find('.')>=0:
			ret = 'Float'
		else:
			ret = 'Int'
	#As every thing in python is object mainly string so default value if unable to recognize above
	else:
		ret = 'String'
	
	return ret

#Evaluate equation
def equation(cline):
	#Evaluate equation using operator used 
	flag=0
	if cline.count('+=') == 1 :
		p1 = cline.find('+=')+1
	elif cline.count('-=') == 1 :
		p1 = cline.find('-=')+1
	elif cline.count('*=') == 1 :
		p1 = cline.find('*=')+1
	elif cline.count('/=') == 1:
		p1 = cline.find('/=')+1
	#for loop equation
	elif cline.find('for ')>=0:
		p1 = cline.find('in')+2
		left  = cline[cline.find('for')+3:p1-2].strip()
		right = cline[p1+1:-1].strip()
		flag=1
	#equation assignment to variable
	elif cline.find('=')>=0:
		p1 = cline.find('=')

	#if not assigned earlier
	if flag==0:
		left = cline[:p1].strip()
		right = cline[p1+1:].strip()
	
	typeDict[left]=rightType(right)
	
	return typeDict[left]

#Finding Multiple assignment with single '=' operator and assign type to each single data
def removenoise():
	dobj = {}
	for d in typeDict:
		if d.find(',')>=0:
			dlist = [x.strip() for x in d.split(',')]
			commalist = []
			if typeDict[d].count(',')==d.count(','):
				commalist = typeDict[d].split(',')
			conum = 0
			for xd in dlist:
				if commalist != []:
					dobj[xd] = commalist[conum]
					conum+=1
				elif typeDict[d]=='List' or typeDict[d]=='Tuple' or typeDict[d]=='Dict':
					dobj[xd]='String'
	typeDict.update(dobj)

#detect assignments and fill data type dictionary with it
def fillTypeDict():
	for i in range(2):
		for l in lines:
			if str(lines.index(l)+1) in key:
				cline=l.strip()
				p0 = cline.find('#')
				if p0>=0:
					cline = cline[:p0].strip()
				
				#importing library assignments
				if cline.count('import')==1 and i==0:
					if cline.count('as')==1:
						p1 = cline.find('as') + 2
						cline = cline[p1:].strip()
						typeDict[cline]=cline
	
				#funtion definition
				elif cline.count('def')==1 and cline.count(':')==1 and i==0:
					p1 = cline.find('(')
					fcline=cline[p1+1:-2]
					parameters = fcline.strip().split(',')
				
					parameters = [x.strip() for x in parameters]
					funpara[str(cline[4:p1].strip())] = parameters
					for pf in parameters:
						if pf.count('=')>0:
						 	equation(pf)
				#Data assignment
				elif cline.count('=') >= 1:
					if  (cline.count('(')==0 and cline.count('.')==0) or cline.find('=')<cline.find('(') or cline.find('=')<cline.find('.'): 
						
						equation(cline)
					elif cline.find('(') < cline.find('='):
						pr1 = cline.find('.')
						dotlist = []
						while pr1>=0:
							bloc = cline[:pr1]
							if bloc.count('(')==bloc.count(')'):
								dotlist.append(bloc)
								cline = cline[pr1+1:]
								pr1 = cline.find('.')
								
							else:
								pr1 = cline.find('.',pr1+1)
						dotlist.append(cline)
						for dp in dotlist:
							if dp.find('(')>0:
								dp = dp[dp.find('(')+1:dp.rfind(')')].split(',')
								for dps in dp:
									if dps.count('=')>0:
										equation(dps)
				#assignment in for loop condition
				elif cline.count('for ') >= 1:
					equation(cline)
		removenoise()
		
		
	
# Evaluate expressions
def findType(exp):
	#left is left side of the expression and right is right side of expressin and op is operator
	op,left,right = '','',''
	
	if exp.find('<')>=0:
		p1 = exp.find('<')
		left += exp[:p1].strip()
		right += exp[p1+1:].strip()
		op+='<'
	elif exp.find('>')>=0:
		p1 = exp.find('>')
		left += exp[:p1].strip()
		right += exp[p1+1:].strip()
		op+='>'
	elif exp.find('!')>=0:
		p1 = exp.find('!')
		right += exp[p1+1:].strip()
		op+='!'	
	elif exp.find('<=')>0:
		p1 = exp.find('<=')
		left += exp[:p1].strip()
		right += exp[p1+2:].strip()
		op+='<='
	elif exp.find('>=')>=0:
		p1 = exp.find('>=')
		left += exp[:p1].strip()
		right += exp[p1+2:].strip()
		op+='>='
	elif exp.find('==')>=0:
		p1 = exp.find('==')
		left += exp[:p1].strip()
		right += exp[p1+2:].strip()
		op+='=='	
	elif exp.find('!=')>=0:
		p1 = exp.find('!=')
		left += exp[:p1].strip()
		right += exp[p1+2:].strip()
		op+='!='
	elif exp.find('in')>=0:
		p1 = exp.find('in')
		left += exp[:p1].strip()
		right += exp[p1+2:].strip()
		op+='in'
	elif exp.find('is')>=0:
		p1 = exp.find('is')
		left += exp[:p1].strip()
		right += exp[p1+2:].strip()
		op+='is'
	elif exp.find('not')==0:
		p1 = exp.find('not')
		right += exp[p1+3:].strip()
		op+='!'
	else:
		return rightType(exp)
		

	ret = ''
	if left!='' and op!='in':
		ret = rightType(left)+' '+op+' '
		
	if op == 'in':
		typeDict[left]=rightType(right)
		return typeDict[left]
	ret += rightType(right)
	return ret


# Evaluation of complex data expression connected using boolean operators
def evaluate(exp):

	cand = exp.count('and ') if exp.find('and ')>-1 else exp.count('& ')	
	cor = exp.count('or ') if exp.find('or ')>-1 else exp.count('| ')
	cnot = exp.find('not ') 
	ret = ''
	if cand+cor==0:
		ret = findType(exp)
	
	elif cand !=0:
		andlist = exp.split('and') if exp.find('and ')>-1 else exp.split('&')
		for al in andlist:
			orlist = al.strip().split('or') if exp.find('or ')>-1 else al.strip().split('|')
			for ol in orlist:
				ret = ret+findType(ol.strip())+' | '
			ret = ret.strip()[:-2]+' & '
		ret=ret.strip()[:-3]
	elif cor != 0:
		orlist = exp.strip().split('or') if exp.find('or ')>-1 else exp.strip().split('|')
		for ol in orlist:
			ret = ret+findType(ol.strip())+' | '
		ret = ret.strip()[:-2]
	return ret

# create labels for states of ASM by evaluating each code lines
def createLabel():
	for i in range(n):
		if str(i+1) in key:
			cline = lines[i].strip()
			p0 = cline.find('#')
			if p0 == 0:
				continue
			elif p0>0:
				cline = cline[:p0].strip()
			
			#While statement
			if cline.count('while')==1:
				p1 = cline.find('while')
				if cline.find('(')>=0:
					cline=cline[p1+6:-2].strip()
				else:
					cline=cline[p1+6:-1].strip()
				data[str(i+1)]['label'] = 'loop('+ evaluate(cline) +')'
				nonParaData[str(i+1)] = 'loop('+ evaluate(cline) +')'
			
			#If statement
			elif cline.count('if')==1:
				p1 = cline.find('if')
				if cline.find('(')>=0 and cline.find('(')<=3:
					cline=cline[p1+3:-2].strip()
				else:
					cline=cline[p1+3:-1].strip()
			
				data[str(i+1)]['label'] = 'if('+ evaluate(cline) +')'
				nonParaData[str(i+1)] = 'if('+ evaluate(cline) +')'

			#Elif statement
			elif cline.count('elif')==1:
				p1 = cline.find('elif')
				if cline.find('(')>=0:
					cline=cline[p1+5:-2].strip()
				else:
					cline=cline[p1+5:-1].strip()

				data[str(i+1)]['label'] = 'elif('+ evaluate(cline) +')'
				nonParaData[str(i+1)] = 'elif('+ evaluate(cline) +')'

			#For statement
			elif cline.count('for')==1:
				p1 = cline.find('in')
				fline = cline[p1+2:-1].strip()
				data[str(i+1)]['label'] = 'loop(' + evaluate(fline) +')'
				nonParaData[str(i+1)] = 'loop('+ evaluate(fline) +')'

			#return statement
			elif cline.count('return')==1:
				p1 = cline.find('return')
				if cline.find('(')>0:
					cline = cline[p1+6:-1].strip()
				else:
					cline =  cline[p1+6:].strip()
				data[str(i+1)]['label'] = 'return('+ evaluate(cline) +')'
				nonParaData[str(i+1)] = 'return('+ evaluate(cline) +')'


			#Method calls assignment to variable
			elif (cline.count('(')>0 and cline.find('=')<cline.find('(')) or (cline.count('.')>0 and cline.find('=')<cline.find('.')):
				
				p1 = cline.find('=')
				right = cline[p1+1:].strip()
				pb = right.find('(')
				if pb == -1:
					pb = right.find('.')
				exp_list = ['[',"'",'"','/','*','+','-','^','&','|']
				st = True
				for ex in exp_list:
					if right.find(ex)!=-1 and pb>right.find(ex):
						st = False
						break
				
				if st==True:
					
					ret = ''
					ret2 = ''
					num = i+1

					#Calls joined using '.' operators
					if right.count('.')>0 and (right.find('.')<right.find('(')):
						dotlist = []
						pr1 = right.find('.')
						while pr1>=0:
							bloc = right[:pr1]
							if bloc.count('(')==bloc.count(')'):
								dotlist.append(bloc)
								right = right[pr1+1:]
								pr1 = right.find('.')
								
							else:
								pr1 = right.find('.',pr1+1)
						dotlist.append(right)
						res=''
						for word in dotlist:
							if word in typeDict:
								res += typeDict[word]+'.'
								ret2 += typeDict[word]+'.'
							else:
								res += typeBracel(word)+'.'
								w1 = word.find('(')
								
								if word[:w1].strip() in typeDict:
									ret2 += typeDict[word[:w1].strip()]+'().'
								elif w1<0:
									ret2 += word.strip()+'.'
								else:
									ret2 += word[:w1].strip()+'().'
						ret2 = ret2[:-1]
						if res[-1]=='.':
							res = res[:-1]	
			
						ret = res
					#Calls having '()'
					else:
						ret = typeBracel(right)
						w1 = right.find('(')
						if right[:w1].strip() in typeDict:
							ret2 += typeDict[right[:w1].strip()]+'()'
						elif w1<0:
							ret2 += right.strip()
						else:
							ret2 += right[:w1].strip()+'()'
						
		
					data[str(num)]['label'] = ret
					nonParaData[str(num)] = ret2

			#Only Method call
			elif (cline.count('(')>0 or cline.count('.')>0):
				p1=cline.find('(')
				p2=cline.find('.')
				ret2 = ''
				# calls connected predominantely by dot operators ex:call1.e1.e2()
				if cline.count('.')>=0 and (p1<0 or p2<p1):
					dotlist = []
					pr1 = cline.find('.')
					'''while(pr1<cline.find('(') and pr1!=-1):
						dotlist.append(cline[:pr1])
						cline = cline[pr1+1:]
						pr1 = cline.find('.')
						print(cline,pr1)'''
					while pr1>=0:
						bloc = cline[:pr1]
						if bloc.count('(')==bloc.count(')'):
							dotlist.append(bloc)
							cline = cline[pr1+1:]
							pr1 = cline.find('.')
							
						else:
							pr1 = cline.find('.',pr1+1)
					
					dotlist.append(cline)
					res=''
					
					for word in dotlist:
						if word in typeDict:
							res += typeDict[word]+'.'
							ret2 += typeDict[word]+'.'
						else:
							res += typeBracel(word)+'.'
							w1 = word.find('(')
							if word[:w1].strip() in typeDict:
								ret2 += typeDict[word[:w1].strip()]+'().'
							elif w1<0:
								ret2 += word.strip()+'.'
							else:
								ret2 += word[:w1].strip()+'().'
							
					
					ret2 = ret2[:-1]	
					if res[-1]=='.':
						res = res[:-1]	
					data[str(i+1)]['label'] = res
					nonParaData[str(i+1)] = ret2
					
				else:
					
					data[str(i+1)]['label'] = typeBracel(cline)
					w1 = cline.find('(')
					if cline[:w1].strip() in typeDict:
						ret2 += typeDict[cline[:w1].strip()]+'()'
					elif w1<0:
						ret2 += cline.strip()
					else:
						ret2 += cline[:w1].strip()+'()'
					nonParaData[str(i+1)] = ret2
					
		

#Remove given state from parents and childrens of any another state
def update_poplist(kdata):
	children = data[str(kdata)]['children']
				
	for k in key:
		c = data[str(k)]['children']
		if kdata in c:
			data[str(k)]['children'].remove(kdata)
			chi = []
			for child in children:
				if str(k) != child and (child not in data[str(k)]['children']): 
					chi.append(child)
			data[str(k)]['children']+=chi
					
			for ch in children:
				if kdata in data[str(ch)]['parent']:
					data[str(ch)]['parent'].remove(kdata)
				if k != ch:
					data[str(ch)]['parent'].append(int(k))
							
		popList.append(str(kdata))			
	
#Remove unnecessary ASM states				
def removeUnnecessaryData():

	for i in range(n):
		if str(i+1) in key:
			cline = lines[i].strip()
			p0 = cline.find('#')
			if p0 == 0:
				continue
			elif p0>0:
				cline = cline[:p0].strip()
			#Unnecessary state containing print statement, function definition, non labelled states , etc.
			if cline.count('print')==1  or ('label' not in data[str(i+1)]) or (cline.count('def')==1 and cline.count(':')==1) or cline.count('sleep'):
				update_poplist(i+1)

	#remove unwanted states using file
	if os.path.exists(filename+'_rstate.txt'):		
		with open(filename+'_rstate.txt') as fp:
			rlist=json.load(fp)
		for fnum in rlist:
			if str(fnum) in key:
				update_poplist(fnum)
	
	#delete unwanted states from machine	
	for p in set(popList):
		del data[str(p)]
	
	
	#remove unnecessary specified states from machine
	ASMkey = data.keys()
	for k in data.keys():
		
		#removes self loops in machine
		data[str(k)]['parent'] = list(set(data[str(k)]['parent']))
		if int(k) in data[str(k)]['parent']:
			data[str(k)]['parent'].remove(int(k))

		data[str(k)]['children'] = list(set(data[str(k)]['children']))
		if int(k) in data[str(k)]['children']:
			data[str(k)]['children'].remove(int(k))

		#removes state from parents and childrens which are not present in ASM anymore
		par = []
		for p in data[str(k)]['parent']:
			if str(p) not in list(data.keys()):
				par.append(p)
		for pr in par:
			data[str(k)]['parent'].remove(pr)

		chil = []
		for c in data[str(k)]['children']:
			if str(c) not in list(data.keys()):
				chil.append(c)
			nextmax = max([int(nk) for nk in data.keys()])
			if len(data[str(k)]['children'])==1 and int(c)<int(k) and int(k)!=nextmax:
				data[str(k)]['children'] = [0]
				'''for nk in data.keys():
					if int(nk)>int(k) and int(nk)<=nextmax:
						nextmax = nk
				data[str(k)]['children'] = [nextmax]
				data[str(nextmax)]['parent'].append(int(k))
				print('*******************',k,nk)'''
		for cr in chil:
			data[str(k)]['children'].remove(cr)


#Main function calls		
fillTypeDict()
createLabel()	
removeUnnecessaryData()	

#Add start state & endstate to ASM 
nkeys = [int(k) for k in list(data.keys()) if k!='0']
min_key = min(nkeys)

if min_key not in data[str(0)]["children"]:
	data[str(0)]["children"].append(min_key)

#start state
data[str(0)]["parent"] = []
data[str(0)]["label"]="start/end" 

#End state
max_key = max(nkeys)
data[str(min_key)]['parent'] = [0]
data[str(max_key)]['children'] = [0]


#remove single parameter found inside method calls
for ki in nonParaData.keys():
	word = nonParaData[str(ki)]
	bword = word.split('.')#to remove types in between bracels
	if word.count(',')>0:
		cp = word.find(',')
		while cp>=0:
			rcp = cp+word[cp+1:].find(')')+1
			lcp = word[:cp].find('(')
			word = word[:lcp+1]+word[rcp:]
			cp = word.find(',')
	else:
		xbw = ''
		
		for bw in bword:
			if bw.count('(')>0 and bw.count(')')>0 and bw.find('(')+1 != bw.find(')'):
				
				xbw += bw+'.'
				xbw = xbw[:xbw.find('(')+1] + xbw[xbw.find(')'):]
			else:
				xbw += bw+'.'
		word = xbw[:-1]		
	nonParaData[str(ki)] = word

#creating non parametric data
noparaData = {}
npdo = {}
npdo["parent"] = []
npdo["children"] = data['0']['children']
npdo["label"]="start/end" 
noparaData[str(0)] = npdo
for k,v in data.items():
	if (k in nonParaData.keys()) and k!='0':
		npd = {}
		npd['parent'] = data[k]['parent']
		npd['children'] = data[k]['children']
		npd['label']=nonParaData[str(k)]
		noparaData[k]=npd
pnList=[]
#removing unlabel states of non parametric data
for knp in data.keys():
	if knp not in noparaData.keys():
			children = data[str(knp)]['children']
				
			for k in noparaData.keys():
				#print(k,noparaData[str(k)])
				c = noparaData[str(k)]['children']
				if knp in c:
					noparaData[str(k)]['children'].remove(knp)
					chi = []
					for child in children:
						if str(k) != child and (child not in noparaData[str(k)]['children']): 
							chi.append(child)
					noparaData[str(k)]['children']+=chi
					
					for ch in children:
						if knp in noparaData[str(ch)]['parent']:
							noparaData[str(ch)]['parent'].remove(knp)
						if k != ch:
							noparaData[str(ch)]['parent'].append(int(k))
							
				pnList.append(str(knp))
for p in set(pnList):
	if str(p) in noparaData.keys():
		del noparaData[str(p)]


'''print('\n\n',filename)
print('ASM: \n\n',data)
print('\n\n')'''
with open(out,'w') as outfile:
	json.dump([data,noparaData],outfile)
#print('ASM created for: ',out,'\n', data)
