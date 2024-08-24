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
        
        # Parse the scan result
        soup = BeautifulSoup(scan_result, 'html.parser')

        # Remove <h1> containing the ZAP logo and report text
        h1_tag = soup.find('h1')
        if h1_tag:
            h1_tag.decompose()

        # Remove specific <h4> containing support information
        h4_tags = soup.find_all('h4')
        for h4_tag in h4_tags:
            if "ZAP is supported by the" in h4_tag.get_text(strip=True):
                h4_tag.decompose()

        # Remove <h3> containing ZAP Version information
        h3_tags = soup.find_all('h3', string=lambda x: x and "ZAP Version:" in x)
        for h3_tag in h3_tags:
            h3_tag.decompose()
        
        # Remove any empty <p> tags that might be present
        empty_p_tags = soup.find_all('p', string='')
        for p_tag in empty_p_tags:
            p_tag.decompose()

        # Extract current site URL from the <h2> tag that lists sites
        h2_tag = soup.find('h2')
        if h2_tag and 'Sites:' in h2_tag.get_text(strip=True):
            sites_text = h2_tag.get_text(strip=True)
            sites_list = sites_text.replace('Sites:', '').strip().split()
            
            # Extract and display the current site only (assuming it's the first one in the list)
            current_site = sites_list[0] if sites_list else 'No site available'
            
            # Update or add an HTML element to display the current site
            new_h2 = soup.new_tag('h2')
            new_h2.string = f"Current Site: {current_site}"
            h2_tag.replace_with(new_h2)

        # Convert the modified HTML back to a string
        parsed_result = soup.prettify()
        
        # Create a new ScanResult entry
        scan_result_entry = ScanResult.objects.create(url=url, result=scan_result, parsed_result=parsed_result)
        
        # Redirect to the results view with the current scan's ID
        return redirect('scan_results_with_id', scan_id=scan_result_entry.id)
       
    return render(request, 'scan/initiate_scan.html')

def scan_results(request, scan_id=None):
    if scan_id:
        result = ScanResult.objects.filter(id=scan_id).first()
    else:
        result = None
    
    return render(request, 'scan/scan_results.html', {'result': result})
