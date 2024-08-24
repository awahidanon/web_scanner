from django.shortcuts import render, redirect
from .models import ScanResult
from zapv2 import ZAPv2
from bs4 import BeautifulSoup

def initiate_scan(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        zap = ZAPv2(apikey='d410bibl7a5cqgmtqgfd90g0md', proxies={'http': 'http://localhost:8080', 'https': 'http://localhost:8080'})
        
        zap.urlopen(url)
        zap.spider.scan(url)
        
        while int(zap.spider.status()) < 100:
            pass

        zap.ascan.scan(url)
        
        while int(zap.ascan.status()) < 100:
            pass
        
        scan_result = zap.core.htmlreport()
        
       
        soup = BeautifulSoup(scan_result, 'html.parser')

       
        h1_tag = soup.find('h1')
        if h1_tag:
            h1_tag.decompose()

        
        h4_tags = soup.find_all('h4')
        for h4_tag in h4_tags:
            if "ZAP is supported by the" in h4_tag.get_text(strip=True):
                h4_tag.decompose()

        
        h3_tags = soup.find_all('h3', string=lambda x: x and "ZAP Version:" in x)
        for h3_tag in h3_tags:
            h3_tag.decompose()
        
        
        empty_p_tags = soup.find_all('p', string='')
        for p_tag in empty_p_tags:
            p_tag.decompose()

       
        h2_tag = soup.find('h2')
        if h2_tag and 'Sites:' in h2_tag.get_text(strip=True):
            sites_text = h2_tag.get_text(strip=True)
            sites_list = sites_text.replace('Sites:', '').strip().split()
            
            
            current_site = sites_list[0] if sites_list else 'No site available'
            
            
            new_h2 = soup.new_tag('h2')
            new_h2.string = f"Current Site: {current_site}"
            h2_tag.replace_with(new_h2)

        
        parsed_result = soup.prettify()
        
       
        scan_result_entry = ScanResult.objects.create(url=url, result=scan_result, parsed_result=parsed_result)
        
       
        return redirect('scan_results_with_id', scan_id=scan_result_entry.id)
       
    return render(request, 'scan/initiate_scan.html')

def scan_results(request, scan_id=None):
    if scan_id:
        result = ScanResult.objects.filter(id=scan_id).first()
    else:
        result = None
    
    return render(request, 'scan/scan_results.html', {'result': result})
