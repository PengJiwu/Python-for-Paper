import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import truncnorm
from sklearn.metrics import auc
import pandas as pd
import itertools

from task import Tasks
from provider import Provider 
from platforms import Platform
from functions import *
import multiprocessing
def plot_satisfaction_distribution(b_rank, b_mean_rank, rank, mean_rank, bar_width):
  #이 plot을 통해서 preference가 더 잘 반영됬다는 것을 알 수 있다. 
  b_pdf, b_cdf = bench_distribution(b_rank)
  pdf, cdf = auctioneer.satisfaction_distribution(rank)
  
  x_axis = np.array(range(len(pdf)))*10
  
  plt.bar(x_axis, pdf, width = bar_width, color = 'r', label = 'proposed')
  plt.bar(x_axis+bar_width, b_pdf, width = bar_width, color ='b', label = 'benchmark')
  plt.vlines(x = (mean_rank / len(b_rank))*100, ymin = 0, ymax = 0.5, color = 'k', linestyles = 'dashed', label = 'Average Rank of Proposed')
  plt.vlines(x = (b_mean_rank / len(b_rank))*100, ymin = 0, ymax = 0.5, color = 'g', linestyles = 'dashdot', label = 'Average Rank of Benchmark')
  plt.xlabel('Rank Range of Matched Providers')
  plt.ylabel('Distribution of Mathced Providers')
  plt.xticks(x_axis)
  plt.ylim([0, 0.5])
  plt.legend(loc = 'best')
  plt.show() 

def Plot_Social_Welfare(task_n, provider_n, max_value, max_alpha, max_deadline, max_task_size, max_mu, max_provider_bid, max_provider_skill, task_columns, provider_columns):
  
  tasks = TaskCreator(task_n, max_value, max_alpha, max_deadline, max_task_size)
  providers = ProviderCreator(provider_n, max_mu, max_provider_bid, max_provider_skill)
  
  pro_exp_social = []
  exp_social = []
  pro_real_social = []
  real_social = []
  
  for i in range(1,11):
    capacity = 20*i
    
    auctioneer = Platform(capacity)

  #platform에서 winners를 선택한다. 
    W_requesters, req_threshold = auctioneer.WinningRequesterSelection(tasks)
    W_providers, pro_threshold = auctioneer.WinningProviderSelection(providers)

  #혹시 모르니깐 requesters와 providers의 숫자를 맞춘다.
    W_requesters, W_providers = auctioneer.Trimming(W_requesters, W_providers)

  #requesters와 providers의 preference ordering을 만든다.
    requester_preference_ordering = auctioneer.ordering_matrix(W_providers,provider_columns)
    provider_preference_ordering = auctioneer.ordering_matrix(W_requesters,task_columns)

    b_rank, b_mean_rank = benchmark_satisfaction_level(requester_preference_ordering)
    b_pdf, b_cdf = bench_distribution(b_rank)

    match = auctioneer.SMA(requester_preference_ordering, provider_preference_ordering)
    #In match, requester: keys, providers: values

    #expected social welfare comparison
    social_welfare = SocialWelfare(W_requesters, W_providers, 0.01, match)
    benchmark = SystemExpectedSocialwelfare(W_requesters, W_providers, 0.01)
    
    pro_exp_social.append(social_welfare)
    exp_social.append(benchmark)
    
    rank, mean_rank = auctioneer.satisfaction_level(match, requester_preference_ordering)
    pdf, cdf = auctioneer.satisfaction_distribution(rank)
    
    #real social welfare
    welfare, t_sub = Proposed_SocialWelfare(W_requesters, W_providers, 0.01, match)
    bench_welfare = Existing_SocialWelfare(W_requesters, W_providers, 0.01)
    
    pro_real_social.append(welfare)
    real_social.append(bench_welfare)
  
  x_axis = np.array(range(1,11))*20
  bar_width = 10
  fig, ax = plt.subplots(nrows = 1, ncols = 2)
  ax[0].bar(x_axis, pro_exp_social, width = bar_width, label = 'proposed exp.SW', color = 'b')
  ax[0].bar(x_axis+bar_width, exp_social, width = bar_width, label = 'benchmark exp.SW', color = 'r')
  ax[0].legend(loc = 'best')
  
  ax[1].bar(x_axis, pro_real_social, width = bar_width, label = 'proposed real.SW', color = 'b')
  ax[1].bar(x_axis+bar_width, real_social, width = bar_width, label = 'benchmark real.SW', color = 'r')
  ax[1].legend(loc = 'best')
  plt.show()  

def SW(time_unit, task_n, provider_n, max_value, max_deadline, max_alpha, max_task_size, max_provider_bid, max_provider_skill, max_mu, task_columns, provider_columns, iteration, capacity, output):

#mere social welfare
  mere1 = []
  mere2 = []

#expected social welfare
  expected1 = []
  expected2 = []
  expected3 = []

#real social welfare
  real1 = []
  real2 = []
  real3 = []

#budget before submission
  before1 = []
  before2 = []
  before3 = []

#budget after submission
  after1 = []
  after2 = []
  after3 = []

#payment before submission
  p_before1 = []
  p_before2 = []
  
#fee before submission
  f_before1 = []
  f_before2 = []

#payment after submission
  p_after1 = []
  p_after2 = []
  p_after3 = []
  
#fee after submission 
  f_after1 = []
  f_after2 = []
  f_after3 = []

#cost
  cost1 = []
  cost2 = []
  
  
  for _ in range(iteration):
    
#participants creation
    tasks = TaskCreator(task_n, max_value, max_alpha, max_deadline, max_task_size)
    providers = ProviderCreator(provider_n, max_mu, max_provider_bid, max_provider_skill)

    auctioneer = Platform(capacity)

#winner selection
#without consideration to alpha and mu
    W_requesters, req_threshold = auctioneer.WinningRequesterSelection(tasks)
    W_providers, pro_threshold = auctioneer.WinningProviderSelection(providers)

#with consideration to alpha and mu
    New_W_requesters, New_req_threshold = auctioneer.New_WinningRequesterSelection(tasks)
    New_W_providers, New_pro_threshold = auctioneer.New_WinningProviderSelection(providers)

#trimming process
    W_requesters, W_providers = auctioneer.Trimming(W_requesters, W_providers)
    New_W_requesters, New_W_providers = auctioneer.Trimming(New_W_requesters, New_W_providers)

    c1 = cost_calculator(W_providers)
    c2 = cost_calculator(New_W_providers)
    
#payment
#temporary payment without consideration to alpha, mu
    payment1 = auctioneer.WPS_payment(W_providers, pro_threshold)
#temporary fee
    fee1 = auctioneer.WRS_payment(W_requesters, req_threshold)
    
    
    
    
    
#temporary payment with consideration to alpha, mu
    payment2 = auctioneer.New_WPS_payment(New_W_providers, New_pro_threshold)
#temporary fee
    fee2 = auctioneer.New_WRS_payment(New_W_requesters, New_req_threshold)



#1. preference ordering
    

#satisfaction level without consideration of preference but with alpha, mu: 2
    New_requester_preference_ordering = auctioneer.ordering_matrix(New_W_providers,provider_columns)
    New_provider_preference_ordering = auctioneer.ordering_matrix(New_W_requesters,task_columns)

    New_r_rank, New_r_mean_rank = benchmark_satisfaction_level(New_requester_preference_ordering)
    New_p_rank, New_p_mean_rank = benchmark_satisfaction_level(New_provider_preference_ordering)

    New_r_pdf, New_r_cdf = bench_distribution(New_r_rank)
    New_p_pdf, New_p_cdf = bench_distribution(New_p_rank)


#Run Stable Marriage Algorithm: In match, requester: keys, providers: values
    match = auctioneer.SMA(New_requester_preference_ordering, New_provider_preference_ordering)

#mere social welfare---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    result = mere_social_welfare(W_requesters) #without consideration to alpha, mu
    result1 = mere_social_welfare(New_W_requesters) #with consideration to alpha, mu
#print('mere social welfare 1: %f' %result)
#print('mere social welfare 2: %f' %result1)

#expected social welfare---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    social_welfare1 = SystemExpectedSocialwelfare(W_requesters, W_providers, time_unit) #without consideration to preference & alpha, mu
    social_welfare2 = SystemExpectedSocialwelfare(New_W_requesters, New_W_providers, time_unit) #with consideration to alpha, mu but without preference
    social_welfare3 = SocialWelfare(New_W_requesters, New_W_providers, time_unit, match) #With consideration to preference & alpha, mu

#print('expected social welfare 1: %f' %social_welfare1)
#print('expected social welfare 2: %f' %social_welfare2)
#print('expected social welfare 3: %f' %social_welfare3)

#print('D 1:%f' %(result-social_welfare1))
#print('D 2:%f' %(result1-social_welfare2))
#print('D 3:%f' %(result1-social_welfare3))


#real social welfare with submission time---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    post_social_welfare1, t_sub1 = Existing_SocialWelfare(W_requesters, W_providers, time_unit) #without consideration to preference, alpha, mu
    post_social_welfare2, t_sub2 = Existing_SocialWelfare(New_W_requesters, New_W_providers, time_unit) #with consideration to alpha, mu
    post_social_welfare3, t_sub3 = Proposed_SocialWelfare(New_W_requesters, New_W_providers, time_unit, match) #with consideration to preference & alpha, mu

#print('real social welfare 1:%f' %post_social_welfare1)
#print('real social welfare 2:%f' %post_social_welfare2)
#print('real social welfare 3:%f' %post_social_welfare3)


#difference between expected social welfare and real social welfare
#print('difference 1: %f' %(social_welfare1-post_social_welfare1))
#print('difference 2: %f' %(social_welfare2-post_social_welfare2))
#print('difference 3: %f' %(social_welfare3-post_social_welfare3))


#budget balance check before submission---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    net_budget1 = budget_balance_check(fee1, payment1) #without consideration to alpha, mu
    net_budget2 = budget_balance_check(fee2, payment2) #with consideration to alpha, mu
    net_budget3 = budget_balance_check(fee2, payment2) #with consideration to alpha, mu and preference

#print('budget before submission(without alpha, mu, preference): %f' %net_budget1)
#print('budget before submission(with alpha and mu): %f' %net_budget2)
#print('budget before submission(with alpha, mu and preference): %f' %net_budget3)

#budget balance after submission---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    changed_fee1, changed_payment1 = bench_time_variant_money(t_sub1, W_requesters, W_providers, fee1, payment1, time_unit)
    changed_fee2, changed_payment2 = bench_time_variant_money(t_sub2, New_W_requesters, New_W_providers, fee2, payment2, time_unit)
    changed_fee3, changed_payment3 = time_variant_money(t_sub3, New_W_requesters, New_W_providers, fee2, payment2, match, time_unit)
    
    
    
    changed_budget1 = budget_balance_check(changed_fee1, changed_payment1) #without consideration to alpha, mu and preference
    changed_budget2 = budget_balance_check(changed_fee2, changed_payment2) #with consideration to alpha, mu
    changed_budget3 = budget_balance_check(changed_fee3, changed_payment3) #with consideration to alpha, mu and preference

#print('budget after submission(without alpha,mu, preference): %f' %changed_budget1)
#print('budget after submission(with alpha,mu): %f' %changed_budget2)
#print('budget after submission(with alpha,mu, preference): %f' %changed_budget3)
 
    #print('iteration: %f, capacity: %f' %(it, unit*(ran+1))) 
 
#budget balance check 
    if net_budget1 < 0:
      result = 0
      social_welfare1 = 0
      post_social_welfare1 = 0
      net_budget1 = 0
      changed_budget1 = 0
      payment1 = 0
      fee1 = 0
      changed_payment1 = 0
      changed_fee1 = 0
      c1 = 0
    
    if net_budget2 < 0:
      result1 = 0
      social_welfare2 = 0; social_welfare3 = 0
      post_social_welfare2 = 0; post_social_welfare3 = 0
      net_budget2 = 0; net_budget3 = 0
      changed_budget2 = 0; changed_budget3 = 0 
      payment2 = 0; fee2 = 0
      changed_payment2 = 0; changed_payment3 = 0
      changed_fee2 = 0; changed_fee3 = 0 
      c2 = 0
      
#mere social welfare
    mere1.append(result)
    mere2.append(result1)

#expected social welfare
    expected1.append(social_welfare1)
    expected2.append(social_welfare2)
    expected3.append(social_welfare3)

#real social welfare
    real1.append(post_social_welfare1)
    real2.append(post_social_welfare2)
    real3.append(post_social_welfare3)

#budget before submission
    before1.append(net_budget1)
    before2.append(net_budget2)
    before3.append(net_budget3)

#budget after submission
    after1.append(changed_budget1)
    after2.append(changed_budget2)
    after3.append(changed_budget3) 
    
#payment before submission
    p_before1.append(np.sum(payment1))
    p_before2.append(np.sum(payment2))
    
#fee before submission   
    f_before1.append(np.sum(fee1))
    f_before2.append(np.sum(fee2))
    
#payment after submission   
    p_after1.append(np.sum(changed_payment1))
    p_after2.append(np.sum(changed_payment2))
    p_after3.append(np.sum(changed_payment3))

#fee after submission    
    f_after1.append(np.sum(changed_fee1))  
    f_after2.append(np.sum(changed_fee2))   
    f_after3.append(np.sum(changed_fee3)) 
    
#cost 
    cost1.append(c1)
    cost2.append(c2)
  
  
  
  
  
  
  #mere social welfare
  mere1 = [x for x in mere1 if x != 0]
  mere2 = [x for x in mere2 if x != 0]#
  if len(mere2) == 0:
    mere2 = 0
#expected social welfare
  expected1 = [x for x in expected1 if x != 0]
  expected2 = [x for x in expected2 if x != 0]#
  expected3 = [x for x in expected3 if x != 0]#
  if len(expected2) == 0:
    expected2 = 0
  if len(expected3) == 0:
    expected3 = 0    
#real social welfare
  real1 = [x for x in real1 if x != 0]
  real2 = [x for x in real2 if x != 0]#
  real3 = [x for x in real3 if x != 0]#
  if len(real2) == 0:
    real2 = 0
  if len(real3) == 0:
    real3 = 0    
#budget before submission
  before1 = [x for x in before1 if x != 0]
  before2 = [x for x in before2 if x != 0]#
  before3 = [x for x in before3 if x != 0]#
  if len(before2) == 0:
    before2 = 0
  if len(before3) == 0:
    before3 = 0    
#budget after submission
  after1 = [x for x in after1 if x != 0]
  after2 = [x for x in after2 if x != 0]#
  after3 = [x for x in after3 if x != 0]#
  if len(after2) == 0:
    after2 = 0
  if len(after3) == 0:
    after3 = 0    
#payment before submission
  p_before1 = [x for x in p_before1 if x != 0]
  p_before2 = [x for x in p_before2 if x != 0]#
  if len(p_before2) == 0:
    p_before2 = 0
#fee before submission
  f_before1 = [x for x in f_before1 if x != 0]
  f_before2 = [x for x in f_before2 if x != 0]#
  if len(f_before2) == 0:
    f_before2 = 0
    
#payment after submission
  p_after1 = [x for x in p_after1 if x != 0]
  p_after2 = [x for x in p_after2 if x != 0]#
  p_after3 = [x for x in p_after3 if x != 0]#
  if len(p_after3) == 0:
    p_after3 = 0
  if len(p_after2) == 0:
    p_after2 = 0
    
#fee after submission 
  f_after1 = [x for x in f_after1 if x != 0]
  f_after2 = [x for x in f_after2 if x != 0]#
  f_after3 = [x for x in f_after3 if x != 0]#
  if len(f_after3) == 0:
    f_after3 = 0
  if len(f_after2) == 0:
    f_after2 = 0  
    
#cost
  cost1 = [x for x in cost1 if x != 0]
  cost2 = [x for x in cost2 if x != 0]#
  
  if len(cost2) == 0:
    cost2 = 0
  
  
  
  #output.put((mere1,mere2,expected1,expected2,expected3,real1,real2,real3,before1,before2, before3, after1, after2, after3, p_before1, p_before2, f_before1, f_before2, p_after1, p_after2, p_after3,
  #f_after1, f_after2, f_after3, cost1, cost2))
   
  output.put((np.mean(mere1), np.mean(mere2), np.mean(expected1), np.mean(expected2), np.mean(expected3), np.mean(real1), np.mean(real2), np.mean(real3), 
  np.mean(before1), np.mean(before2), np.mean(before3), np.mean(after1), np.mean(after2), np.mean(after3), np.mean(p_before1), np.mean(p_before2), np.mean(f_before1), 
  np.mean(f_before2), np.mean(p_after1), np.mean(p_after2), np.mean(p_after3), np.mean(f_after1), np.mean(f_after2), np.mean(f_after3), np.mean(cost1), np.mean(cost2)))
   
  
#항상 3가지 case에 대해서 생각하자.
#1. without consideration to preference & alpha, mu
#2. with consideration to alpha, mu but without preference
#3. with consideration to preference & alpha, mu

if __name__ == "__main__":

#iteration
  iteration = 3

#capacity unit & range
  unit = 1
  ranges = 4

  

#time_unit setting
  time_unit = 0.01

#sample을 몇 개를 생성할지 정하자 
  provider_n = 2000
  task_n = 1000
#task_info 설정
  max_value = 80
  max_deadline = 100
  #나중에 max_alpha를 변화시키면서 한 번 보자
  max_task_size = 10

#provider bid & skill 정보를 설정
  max_provider_bid = 10 
  max_provider_skill = 10
  max_mu = 1 #이 값도 한 번 변화시키서 보자.

#column information
  task_columns = ['alpha', 'deadline', 'bid to size ratio']
  provider_columns = ['mu','bid','skill']
 
  x_axis = [0.01*(10**x) for x in np.arange(0, ranges, unit)]
  x_axis = np.around(x_axis, decimals = 2)
  num_core = multiprocessing.cpu_count() - 1
  
  
  result = []
  #output = queue to store the results from each core
  #processor
  
  cap = 300
  
  for max_alpha in x_axis:
    
    print(max_alpha)
    tmp_result = []
    outputs = []
    process = []
    
    for _ in range(num_core):
      outputs.append(multiprocessing.Queue())

    for i in range(num_core):
      
      process.append(multiprocessing.Process(target = SW, args = (time_unit, task_n, provider_n, max_value, max_deadline, 
      max_alpha, max_task_size, max_provider_bid, max_provider_skill, max_mu, task_columns, provider_columns, iteration, cap, outputs[i])))
  
    for pro in process:
      pro.start()

    for i in range(num_core):
      tmp_result.append(outputs[i].get())  

    for i in range(num_core):
      outputs[i].close()  
  
    for pro in process:
      pro.terminate()  
    
    result.append(np.mean(tmp_result, axis = 0)) 
    
  columns = ['mere1', 'mere2', 'expected1','expected2','expected3','real1','real2','real3','before1','before2','before3','after1','after2','after3', 'p_before1', 'p_before2', 'f_before1', 'f_before2', 'p_after1', 'p_after2', 'p_after3', 'f_after1', 'f_after2', 'f_after3', 'cost1', 'cost2']
  
  result = pd.DataFrame(result, columns = columns, index = x_axis)
  result.to_pickle('alpha_result.pkl') 
  print(result.to_string())
