#!/usr/bin/env python3
"""
Backend API tests for Admin Panel (SEO + Blog CMS)
Tests all endpoints in /app/backend/seo_admin.py
"""
import requests
import json
import sys

# Backend URL from frontend/.env
BASE_URL = "https://abced79c-6e9c-40cc-8d66-2e065bc1abab.preview.emergentagent.com/api"

# Admin credentials from /app/memory/test_credentials.md
ADMIN_EMAIL = "admin@lovepdf.com"
ADMIN_PASSWORD = "Admin@12345"

# Test results tracking
passed = 0
failed = 0
test_results = []

def log_test(name, success, details=""):
    global passed, failed
    if success:
        passed += 1
        status = "✅ PASS"
    else:
        failed += 1
        status = "❌ FAIL"
    msg = f"{status}: {name}"
    if details:
        msg += f" - {details}"
    print(msg)
    test_results.append({"name": name, "success": success, "details": details})

def test_auth():
    """Test authentication endpoints"""
    print("\n" + "="*60)
    print("1. TESTING AUTH ENDPOINTS")
    print("="*60)
    
    token = None
    
    # Test 1: Login with correct credentials
    try:
        resp = requests.post(f"{BASE_URL}/admin/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if "access_token" in data and "email" in data:
                token = data["access_token"]
                log_test("POST /api/admin/login (correct creds)", True, f"Got token, email={data['email']}")
            else:
                log_test("POST /api/admin/login (correct creds)", False, "Missing access_token or email in response")
        else:
            log_test("POST /api/admin/login (correct creds)", False, f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("POST /api/admin/login (correct creds)", False, str(e))
    
    # Test 2: Login with wrong password
    try:
        resp = requests.post(f"{BASE_URL}/admin/login", json={
            "email": ADMIN_EMAIL,
            "password": "WrongPassword123"
        }, timeout=10)
        
        if resp.status_code == 401:
            log_test("POST /api/admin/login (wrong password)", True, "Correctly returned 401")
        else:
            log_test("POST /api/admin/login (wrong password)", False, f"Expected 401, got {resp.status_code}")
    except Exception as e:
        log_test("POST /api/admin/login (wrong password)", False, str(e))
    
    # Test 3: GET /admin/me WITHOUT token
    try:
        resp = requests.get(f"{BASE_URL}/admin/me", timeout=10)
        if resp.status_code == 401:
            log_test("GET /api/admin/me (without token)", True, "Correctly returned 401")
        else:
            log_test("GET /api/admin/me (without token)", False, f"Expected 401, got {resp.status_code}")
    except Exception as e:
        log_test("GET /api/admin/me (without token)", False, str(e))
    
    # Test 4: GET /admin/me WITH token
    if token:
        try:
            me_resp = requests.get(f"{BASE_URL}/admin/me", 
                                  headers={"Authorization": f"Bearer {token}"},
                                  timeout=10)
            if me_resp.status_code == 200:
                me_data = me_resp.json()
                if "email" in me_data:
                    log_test("GET /api/admin/me (with token)", True, f"email={me_data['email']}")
                else:
                    log_test("GET /api/admin/me (with token)", False, "Missing email in response")
            else:
                log_test("GET /api/admin/me (with token)", False, f"Status {me_resp.status_code}: {me_resp.text}")
        except Exception as e:
            log_test("GET /api/admin/me (with token)", False, str(e))
    else:
        log_test("GET /api/admin/me (with token)", False, "No token available from login")
    
    return token  # Return token for subsequent tests

def test_seo_pages(token):
    """Test SEO pages CRUD endpoints"""
    print("\n" + "="*60)
    print("2. TESTING SEO PAGES ENDPOINTS")
    print("="*60)
    
    if not token:
        log_test("SEO Pages tests", False, "No auth token available")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: PUT /api/admin/seo/pages (upsert)
    try:
        resp = requests.put(f"{BASE_URL}/admin/seo/pages", 
                           headers=headers,
                           json={
                               "path": "/tool/merge-pdf",
                               "title": "Test Merge PDF",
                               "description": "Test description",
                               "keywords": "merge, pdf, test"
                           },
                           timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok") and data.get("path") == "/tool/merge-pdf":
                log_test("PUT /api/admin/seo/pages", True, "SEO page saved")
            else:
                log_test("PUT /api/admin/seo/pages", False, f"Unexpected response: {data}")
        else:
            log_test("PUT /api/admin/seo/pages", False, f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("PUT /api/admin/seo/pages", False, str(e))
    
    # Test 2: GET /api/admin/seo/pages (list)
    try:
        resp = requests.get(f"{BASE_URL}/admin/seo/pages", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if "pages" in data:
                pages = data["pages"]
                found = any(p.get("path") == "/tool/merge-pdf" for p in pages)
                if found:
                    log_test("GET /api/admin/seo/pages", True, f"Found saved path in list ({len(pages)} pages)")
                else:
                    log_test("GET /api/admin/seo/pages", False, "Saved path not found in list")
            else:
                log_test("GET /api/admin/seo/pages", False, "Missing 'pages' in response")
        else:
            log_test("GET /api/admin/seo/pages", False, f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("GET /api/admin/seo/pages", False, str(e))
    
    # Test 3: Public GET /api/seo/page
    try:
        resp = requests.get(f"{BASE_URL}/seo/page?path=/tool/merge-pdf", timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if "seo" in data and data["seo"]:
                seo = data["seo"]
                if seo.get("title") == "Test Merge PDF":
                    log_test("GET /api/seo/page (public)", True, "SEO data reflects saved title")
                else:
                    log_test("GET /api/seo/page (public)", False, f"Title mismatch: {seo.get('title')}")
            else:
                log_test("GET /api/seo/page (public)", False, "No SEO data returned")
        else:
            log_test("GET /api/seo/page (public)", False, f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("GET /api/seo/page (public)", False, str(e))

def test_site_settings(token):
    """Test site settings endpoints"""
    print("\n" + "="*60)
    print("3. TESTING SITE SETTINGS ENDPOINTS")
    print("="*60)
    
    if not token:
        log_test("Site Settings tests", False, "No auth token available")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: GET /api/admin/site
    try:
        resp = requests.get(f"{BASE_URL}/admin/site", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if "site" in data:
                log_test("GET /api/admin/site", True, "Site settings retrieved")
            else:
                log_test("GET /api/admin/site", False, "Missing 'site' in response")
        else:
            log_test("GET /api/admin/site", False, f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("GET /api/admin/site", False, str(e))
    
    # Test 2: PUT /api/admin/site
    try:
        resp = requests.put(f"{BASE_URL}/admin/site",
                           headers=headers,
                           json={
                               "site_name": "LovePDF Test",
                               "site_url": "https://example.com",
                               "ga_measurement_id": "G-TEST123"
                           },
                           timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok"):
                log_test("PUT /api/admin/site", True, "Site settings updated")
            else:
                log_test("PUT /api/admin/site", False, f"Unexpected response: {data}")
        else:
            log_test("PUT /api/admin/site", False, f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("PUT /api/admin/site", False, str(e))
    
    # Test 3: Public GET /api/seo/site
    try:
        resp = requests.get(f"{BASE_URL}/seo/site", timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if "site" in data:
                site = data["site"]
                if site.get("site_name") == "LovePDF Test" and site.get("ga_measurement_id") == "G-TEST123":
                    log_test("GET /api/seo/site (public)", True, "Site settings reflect saved values")
                else:
                    log_test("GET /api/seo/site (public)", False, f"Values mismatch: {site}")
            else:
                log_test("GET /api/seo/site (public)", False, "Missing 'site' in response")
        else:
            log_test("GET /api/seo/site (public)", False, f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("GET /api/seo/site (public)", False, str(e))

def test_blog(token):
    """Test blog CRUD endpoints"""
    print("\n" + "="*60)
    print("4. TESTING BLOG ENDPOINTS")
    print("="*60)
    
    if not token:
        log_test("Blog tests", False, "No auth token available")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    post_id = None
    
    # Test 1: POST /api/admin/blog (create)
    try:
        resp = requests.post(f"{BASE_URL}/admin/blog",
                            headers=headers,
                            json={
                                "slug": "hello-world-test",
                                "title": "Hello World Test",
                                "content": "<p>Test content</p>",
                                "published": True
                            },
                            timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok") and "id" in data:
                post_id = data["id"]
                log_test("POST /api/admin/blog (create)", True, f"Post created with id={post_id}")
            else:
                log_test("POST /api/admin/blog (create)", False, f"Unexpected response: {data}")
        else:
            log_test("POST /api/admin/blog (create)", False, f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("POST /api/admin/blog (create)", False, str(e))
    
    # Test 2: POST same slug again (should fail with 400)
    try:
        resp = requests.post(f"{BASE_URL}/admin/blog",
                            headers=headers,
                            json={
                                "slug": "hello-world-test",
                                "title": "Duplicate",
                                "content": "<p>Duplicate</p>",
                                "published": True
                            },
                            timeout=10)
        
        if resp.status_code == 400:
            log_test("POST /api/admin/blog (duplicate slug)", True, "Correctly returned 400 for duplicate slug")
        else:
            log_test("POST /api/admin/blog (duplicate slug)", False, f"Expected 400, got {resp.status_code}")
    except Exception as e:
        log_test("POST /api/admin/blog (duplicate slug)", False, str(e))
    
    # Test 3: GET /api/admin/blog (list all)
    try:
        resp = requests.get(f"{BASE_URL}/admin/blog", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if "posts" in data:
                posts = data["posts"]
                found = any(p.get("slug") == "hello-world-test" for p in posts)
                if found:
                    log_test("GET /api/admin/blog", True, f"Found created post in list ({len(posts)} posts)")
                else:
                    log_test("GET /api/admin/blog", False, "Created post not found in list")
            else:
                log_test("GET /api/admin/blog", False, "Missing 'posts' in response")
        else:
            log_test("GET /api/admin/blog", False, f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("GET /api/admin/blog", False, str(e))
    
    # Test 4: PUT /api/admin/blog/{id} (update)
    if post_id:
        try:
            resp = requests.put(f"{BASE_URL}/admin/blog/{post_id}",
                               headers=headers,
                               json={
                                   "slug": "hello-world-test",
                                   "title": "Hello World Updated",
                                   "content": "<p>Updated content</p>",
                                   "published": True
                               },
                               timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    log_test("PUT /api/admin/blog/{id} (update)", True, "Post updated")
                else:
                    log_test("PUT /api/admin/blog/{id} (update)", False, f"Unexpected response: {data}")
            else:
                log_test("PUT /api/admin/blog/{id} (update)", False, f"Status {resp.status_code}: {resp.text}")
        except Exception as e:
            log_test("PUT /api/admin/blog/{id} (update)", False, str(e))
    else:
        log_test("PUT /api/admin/blog/{id} (update)", False, "No post_id available")
    
    # Test 5: Public GET /api/blog (list published)
    try:
        resp = requests.get(f"{BASE_URL}/blog", timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if "posts" in data:
                posts = data["posts"]
                found = any(p.get("slug") == "hello-world-test" for p in posts)
                # Check that content field is excluded
                has_content = any("content" in p for p in posts)
                if found and not has_content:
                    log_test("GET /api/blog (public list)", True, f"Published post found, content excluded ({len(posts)} posts)")
                elif found and has_content:
                    log_test("GET /api/blog (public list)", False, "Content field should be excluded from list")
                else:
                    log_test("GET /api/blog (public list)", False, "Published post not found")
            else:
                log_test("GET /api/blog (public list)", False, "Missing 'posts' in response")
        else:
            log_test("GET /api/blog (public list)", False, f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("GET /api/blog (public list)", False, str(e))
    
    # Test 6: Public GET /api/blog/{slug} (detail)
    try:
        resp = requests.get(f"{BASE_URL}/blog/hello-world-test", timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if "post" in data:
                post = data["post"]
                if post.get("title") == "Hello World Updated" and "content" in post:
                    log_test("GET /api/blog/{slug} (public detail)", True, "Full post with updated title and content")
                else:
                    log_test("GET /api/blog/{slug} (public detail)", False, f"Data mismatch: {post}")
            else:
                log_test("GET /api/blog/{slug} (public detail)", False, "Missing 'post' in response")
        else:
            log_test("GET /api/blog/{slug} (public detail)", False, f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("GET /api/blog/{slug} (public detail)", False, str(e))
    
    # Test 7: DELETE /api/admin/blog/{id}
    if post_id:
        try:
            resp = requests.delete(f"{BASE_URL}/admin/blog/{post_id}",
                                  headers=headers,
                                  timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    log_test("DELETE /api/admin/blog/{id}", True, "Post deleted")
                    
                    # Test 8: Verify public GET returns 404 after delete
                    try:
                        verify_resp = requests.get(f"{BASE_URL}/blog/hello-world-test", timeout=10)
                        if verify_resp.status_code == 404:
                            log_test("GET /api/blog/{slug} after delete", True, "Correctly returns 404")
                        else:
                            log_test("GET /api/blog/{slug} after delete", False, f"Expected 404, got {verify_resp.status_code}")
                    except Exception as e:
                        log_test("GET /api/blog/{slug} after delete", False, str(e))
                else:
                    log_test("DELETE /api/admin/blog/{id}", False, f"Unexpected response: {data}")
            else:
                log_test("DELETE /api/admin/blog/{id}", False, f"Status {resp.status_code}: {resp.text}")
        except Exception as e:
            log_test("DELETE /api/admin/blog/{id}", False, str(e))
    else:
        log_test("DELETE /api/admin/blog/{id}", False, "No post_id available")
    
    # Test 9: Verify admin blog routes require auth
    try:
        resp = requests.get(f"{BASE_URL}/admin/blog", timeout=10)
        if resp.status_code == 401:
            log_test("GET /api/admin/blog (no auth)", True, "Correctly returns 401 without token")
        else:
            log_test("GET /api/admin/blog (no auth)", False, f"Expected 401, got {resp.status_code}")
    except Exception as e:
        log_test("GET /api/admin/blog (no auth)", False, str(e))

def test_seo_infra():
    """Test sitemap.xml and robots.txt"""
    print("\n" + "="*60)
    print("5. TESTING SEO INFRASTRUCTURE")
    print("="*60)
    
    # Test 1: GET /api/sitemap.xml
    try:
        resp = requests.get(f"{BASE_URL}/sitemap.xml", timeout=10)
        
        if resp.status_code == 200:
            content = resp.text
            if '<?xml version="1.0"' in content and '<urlset' in content:
                # Check for tool URLs
                has_tools = '/tool/' in content
                if has_tools:
                    log_test("GET /api/sitemap.xml", True, "Valid XML with tool URLs")
                else:
                    log_test("GET /api/sitemap.xml", False, "Missing tool URLs in sitemap")
            else:
                log_test("GET /api/sitemap.xml", False, "Invalid XML format")
        else:
            log_test("GET /api/sitemap.xml", False, f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("GET /api/sitemap.xml", False, str(e))
    
    # Test 2: GET /api/robots.txt
    try:
        resp = requests.get(f"{BASE_URL}/robots.txt", timeout=10)
        
        if resp.status_code == 200:
            content = resp.text
            has_disallow_admin = "Disallow: /admin" in content
            has_sitemap = "Sitemap:" in content
            if has_disallow_admin and has_sitemap:
                log_test("GET /api/robots.txt", True, "Contains Disallow: /admin and Sitemap line")
            else:
                log_test("GET /api/robots.txt", False, f"Missing required content. Has admin: {has_disallow_admin}, Has sitemap: {has_sitemap}")
        else:
            log_test("GET /api/robots.txt", False, f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        log_test("GET /api/robots.txt", False, str(e))

def main():
    print("="*60)
    print("ADMIN PANEL BACKEND API TESTS")
    print("="*60)
    print(f"Backend URL: {BASE_URL}")
    print(f"Admin Email: {ADMIN_EMAIL}")
    print("="*60)
    
    # Run all tests
    token = test_auth()
    test_seo_pages(token)
    test_site_settings(token)
    test_blog(token)
    test_seo_infra()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total: {passed + failed} tests")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print("="*60)
    
    if failed > 0:
        print("\nFAILED TESTS:")
        for result in test_results:
            if not result["success"]:
                print(f"  - {result['name']}: {result['details']}")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
