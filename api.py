import json
import requests
import time
import re

# ==========================================
# CẤU HÌNH TOKEN TỪ TOOL TELEGRAM
# ==========================================
TOKEN_SETS = [
    {
        "fetch_token": "eyJhbGciOiJFUzI1NiIsIng1YyI6WyJNSUlFTVRDQ0E3YWdBd0lCQWdJUVI4S0h6ZG41NTRaL1VvcmFkTng5dHpBS0JnZ3Foa2pPUFFRREF6QjFNVVF3UWdZRFZRUURERHRCY0hCc1pTQlhiM0pzWkhkcFpHVWdSR1YyWld4dmNHVnlJRkpsYkdGMGFXOXVjeUJEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURUxNQWtHQTFVRUN3d0NSell4RXpBUkJnTlZCQW9NQ2tGd2NHeGxJRWx1WXk0eEN6QUpCZ05WQkFZVEFsVlRNQjRYRFRJMU1Ea3hPVEU1TkRRMU1Wb1hEVEkzTVRBeE16RTNORGN5TTFvd2daSXhRREErQmdOVkJBTU1OMUJ5YjJRZ1JVTkRJRTFoWXlCQmNIQWdVM1J2Y21VZ1lXNWtJR2xVZFc1bGN5QlRkRzl5WlNCU1pXTmxhWEIwSUZOcFoyNXBibWN4TERBcUJnTlZCQXNNSTBGd2NHeGxJRmR2Y214a2QybGtaU0JFWlhabGJHOXdaWElnVW1Wc1lYUnBiMjV6TVJNd0VRWURWUVFLREFwQmNIQnNaU0JKYm1NdU1Rc3dDUVlEVlFRR0V3SlZVekJaTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEEwSUFCTm5WdmhjdjdpVCs3RXg1dEJNQmdyUXNwSHpJc1hSaTBZeGZlazdsdjh3RW1qL2JIaVd0TndKcWMyQm9IenNRaUVqUDdLRklJS2c0WTh5MC9ueW51QW1qZ2dJSU1JSUNCREFNQmdOVkhSTUJBZjhFQWpBQU1COEdBMVVkSXdRWU1CYUFGRDh2bENOUjAxREptaWc5N2JCODVjK2xrR0taTUhBR0NDc0dBUVVGQndFQkJHUXdZakF0QmdnckJnRUZCUWN3QW9ZaGFIUjBjRG92TDJObGNuUnpMbUZ3Y0d4bExtTnZiUzkzZDJSeVp6WXVaR1Z5TURFR0NDc0dBUVVGQnpBQmhpVm9kSFJ3T2k4dmIyTnpjQzVoY0hCc1pTNWpiMjB2YjJOemNEQXpMWGQzWkhKbk5qQXlNSUlCSGdZRFZSMGdCSUlCRlRDQ0FSRXdnZ0VOQmdvcWhraUc5Mk5rQlFZQk1JSCtNSUhEQmdnckJnRUZCUWNDQWpDQnRneUJzMUpsYkdsaGJtTmxJRzl1SUhSb2FYTWdZMlZ5ZEdsbWFXTmhkR1VnWW5rZ1lXNTVJSEJoY25SNUlHRnpjM1Z0WlhNZ1lXTmpaWEIwWVc1alpTQnZaaUIwYUdVZ2RHaGxiaUJoY0hCc2FXTmhZbXhsSUhOMFlXNWtZWEprSUhSbGNtMXpJR0Z1WkNCamIyNWthWFJwYjI1eklHOW1JSFZ6WlN3Z1kyVnlkR2xtYVdOaGRHVWdjRzlzYVdONUlHRnVaQ0JqWlhKMGFXWnBZMkYwYVc5dUlIQnlZV04wYVdObElITjBZWFJsYldWdWRITXVNRFlHQ0NzR0FRVUZCd0lCRmlwb2RIUndPaTh2ZDNkM0xtRndjR3hsTG1OdmJTOWpaWEowYVdacFkyRjBaV0YxZEdodmNtbDBlUzh3SFFZRFZSME9CQllFRklGaW9HNHdNTVZBMWt1OXpKbUdOUEFWbjNlcU1BNEdBMVVkRHdFQi93UUVBd0lIZ0RBUUJnb3Foa2lHOTJOa0Jnc0JCQUlGQURBS0JnZ3Foa2pPUFFRREF3TnBBREJtQWpFQStxWG5SRUM3aFhJV1ZMc0x4em5qUnBJelBmN1ZIejlWL0NUbTgrTEpsclFlcG5tY1B2R0xOY1g2WFBubGNnTEFBakVBNUlqTlpLZ2c1cFE3OWtuRjRJYlRYZEt2OHZ1dElETVhEbWpQVlQzZEd2RnRzR1J3WE95d1Iya1pDZFNyZmVvdCIsIk1JSURGakNDQXB5Z0F3SUJBZ0lVSXNHaFJ3cDBjMm52VTRZU3ljYWZQVGp6Yk5jd0NnWUlLb1pJemowRUF3TXdaekViTUJrR0ExVUVBd3dTUVhCd2JHVWdVbTl2ZENCRFFTQXRJRWN6TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd0hoY05NakV3TXpFM01qQXpOekV3V2hjTk16WXdNekU1TURBd01EQXdXakIxTVVRd1FnWURWUVFERER0QmNIQnNaU0JYYjNKc1pIZHBaR1VnUkdWMlpXeHZjR1Z5SUZKbGJHRjBhVzl1Y3lCRFpYSjBhV1pwWTJGMGFXOXVJRUYxZEdodmNtbDBlVEVMTUFrR0ExVUVDd3dDUnpZeEV6QVJCZ05WQkFvTUNrRndjR3hsSUVsdVl5NHhDekFKQmdOVkJBWVRBbFZUTUhZd0VBWUhLb1pJemowQ0FRWUZLNEVFQUNJRFlnQUVic1FLQzk0UHJsV21aWG5YZ3R4emRWSkw4VDBTR1luZ0RSR3BuZ24zTjZQVDhKTUViN0ZEaTRiQm1QaENuWjMvc3E2UEYvY0djS1hXc0w1dk90ZVJoeUo0NXgzQVNQN2NPQithYW85MGZjcHhTdi9FWkZibmlBYk5nWkdoSWhwSW80SDZNSUgzTUJJR0ExVWRFd0VCL3dRSU1BWUJBZjhDQVFBd0h3WURWUjBqQkJnd0ZvQVV1N0Rlb1ZnemlKcWtpcG5ldnIzcnI5ckxKS3N3UmdZSUt3WUJCUVVIQVFFRU9qQTRNRFlHQ0NzR0FRVUZCekFCaGlwb2RIUndPaTh2YjJOemNDNWhjSEJzWlM1amIyMHZiMk56Y0RBekxXRndjR3hsY205dmRHTmhaek13TndZRFZSMGZCREF3TGpBc29DcWdLSVltYUhSMGNEb3ZMMk55YkM1aGNIQnNaUzVqYjIwdllYQndiR1Z5YjI5MFkyRm5NeTVqY213d0hRWURWUjBPQkJZRUZEOHZsQ05SMDFESm1pZzk3YkI4NWMrbGtHS1pNQTRHQTFVZER3RUIvd1FFQXdJQkJqQVFCZ29xaGtpRzkyTmtCZ0lCQkFJRkFEQUtCZ2dxaGtqT1BRUURBd05vQURCbEFqQkFYaFNxNUl5S29nTUNQdHc0OTBCYUI2NzdDYUVHSlh1ZlFCL0VxWkdkNkNTamlDdE9udU1UYlhWWG14eGN4ZmtDTVFEVFNQeGFyWlh2TnJreFUzVGtVTUkzM3l6dkZWVlJUNHd4V0pDOTk0T3NkY1o0K1JHTnNZRHlSNWdtZHIwbkRHZz0iLCJNSUlDUXpDQ0FjbWdBd0lCQWdJSUxjWDhpTkxGUzVVd0NnWUlLb1pJemowRUF3TXdaekViTUJrR0ExVUVBd3dTUVhCd2JHVWdVbTl2ZENCRFFTQXRJRWN6TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd0hoY05NVFF3TkRNd01UZ3hPVEEyV2hjTk16a3dORE13TVRneE9UQTJXakJuTVJzd0dRWURWUVFEREJKQmNIQnNaU0JTYjI5MElFTkJJQzBnUnpNeEpqQWtCZ05WQkFzTUhVRndjR3hsSUVObGNuUnBabWxqWVhScGIyNGdRWFYwYUc5eWFYUjVNUk13RVFZRFZRUUtEQXBCY0hCc1pTQkpibU11TVFzd0NRWURWUVFHRXdKVlV6QjJNQkFHQnlxR1NNNDlBZ0VHQlN1QkJBQWlBMklBQkpqcEx6MUFjcVR0a3lKeWdSTWMzUkNWOGNXalRuSGNGQmJaRHVXbUJTcDNaSHRmVGpqVHV4eEV0WC8xSDdZeVlsM0o2WVJiVHpCUEVWb0EvVmhZREtYMUR5eE5CMGNUZGRxWGw1ZHZNVnp0SzUxN0lEdll1VlRaWHBta09sRUtNYU5DTUVBd0hRWURWUjBPQkJZRUZMdXczcUZZTTRpYXBJcVozcjY5NjYvYXl5U3JNQThHQTFVZEV3RUIvd1FGTUFNQkFmOHdEZ1lEVlIwUEFRSC9CQVFEQWdFR01Bb0dDQ3FHU000OUJBTURBMmdBTUdVQ01RQ0Q2Y0hFRmw0YVhUUVkyZTN2OUd3T0FFWkx1Tit5UmhIRkQvM21lb3locG12T3dnUFVuUFdUeG5TNGF0K3FJeFVDTUcxbWloREsxQTNVVDgyTlF6NjBpbU9sTTI3amJkb1h0MlFmeUZNbStZaGlkRGtMRjF2TFVhZ002QmdENTZLeUtBPT0iXX0.eyJ0cmFuc2FjdGlvbklkIjoiNjAwMDMzNDI2MjAxMjkiLCJvcmlnaW5hbFRyYW5zYWN0aW9uSWQiOiI2MDAwMzM0MjYyMDEyOSIsIndlYk9yZGVyTGluZUl0ZW1JZCI6IjYwMDAxMzc2MzAzMTM1IiwiYnVuZGxlSWQiOiJjb20ubG9ja2V0LkxvY2tldCIsInByb2R1Y3RJZCI6ImxvY2tldF8xOTlfMW0iLCJzdWJzY3JpcHRpb25Hcm91cElkZW50aWZpZXIiOiIyMTQxOTQ0NyIsInB1cmNoYXNlRGF0ZSI6MTc4Nzg1MjQwNzAwMCwib3JpZ2luYWxQdXJjaGFzZURhdGUiOjE3ODc4NTI0MDcwMDAsImV4cGlyZXNEYXRlIjoxNzkwNTMwODA3MDAwLCJxdWFudGl0eSI6MSwidHlwZSI6IkF1dG8tUmVuZXdhYmxlIFN1YnNjcmlwdGlvbiIsImRldmljZVZlcmlmaWNhdGlvbiI6ImRtNFhNV01ENk9Mbkl1K0hMcDg2RElFVnc3VWNEcWpVQVJhc0xtV2dpQVpoajBsTGJqR3AvZWdmWVo3aHcyTEciLCJkZXZpY2VWZXJpZmljYXRpb25Ob25jZSI6ImY4YTQ5ZjhlLTkxYmMtNGIwMi04OGYyLWEwZDI5M2YwMDE2MSIsImluQXBwT3duZXJzaGlwVHlwZSI6IlBVUkNIQVNFRCIsInNpZ25lZERhdGUiOjE3ODc4NTI0OTA5NjMsImVudmlyb25tZW50IjoiUHJvZHVjdGlvbiIsInRyYW5zYWN0aW9uUmVhc29uIjoiUFVSQ0hBU0UiLCJzdG9yZWZyb250IjoiVk5NIiwic3RvcmVmcm9udElkIjoiMTQzNDcxIiwicHJpY2UiOjQ5MDAwMDAwLCJjdXJyZW5jeSI6IlZORCIsImFwcFRyYW5zYWN0aW9uSWQiOiI3MDUyODY5NTM4NTgzNjQ3NDciLCJiaWxsaW5nUGxhblR5cGUiOiJCSUxMRURfVVBGUk9OVCJ9.skp6gi1KsipfHM56ULbPvXAu_-Wml5quX5JZgbFdRs7DNvVcfFEVtHngHFo1f2IUlZ7Zyeom1rw9fMMa-W26wA",
        "app_transaction": "eyJhbGciOiJFUzI1NiIsIng1YyI6WyJNSUlFTVRDQ0E3YWdBd0lCQWdJUVI4S0h6ZG41NTRaL1VvcmFkTng5dHpBS0JnZ3Foa2pPUFFRREF6QjFNVVF3UWdZRFZRUURERHRCY0hCc1pTQlhiM0pzWkhkcFpHVWdSR1YyWld4dmNHVnlJRkpsYkdGMGFXOXVjeUJEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURUxNQWtHQTFVRUN3d0NSell4RXpBUkJnTlZCQW9NQ2tGd2NHeGxJRWx1WXk0eEN6QUpCZ05WQkFZVEFsVlRNQjRYRFRJMU1Ea3hPVEU1TkRRMU1Wb1hEVEkzTVRBeE16RTNORGN5TTFvd2daSXhRREErQmdOVkJBTU1OMUJ5YjJRZ1JVTkRJRTFoWXlCQmNIQWdVM1J2Y21VZ1lXNWtJR2xVZFc1bGN5QlRkRzl5WlNCU1pXTmxhWEIwSUZOcFoyNXBibWN4TERBcUJnTlZCQXNNSTBGd2NHeGxJRmR2Y214a2QybGtaU0JFWlhabGJHOXdaWElnVW1Wc1lYUnBiMjV6TVJNd0VRWURWUVFLREFwQmNIQnNaU0JKYm1NdU1Rc3dDUVlEVlFRR0V3SlZVekJaTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEEwSUFCTm5WdmhjdjdpVCs3RXg1dEJNQmdyUXNwSHpJc1hSaTBZeGZlazdsdjh3RW1qL2JIaVd0TndKcWMyQm9IenNRaUVqUDdLRklJS2c0WTh5MC9ueW51QW1qZ2dJSU1JSUNCREFNQmdOVkhSTUJBZjhFQWpBQU1COEdBMVVkSXdRWU1CYUFGRDh2bENOUjAxREptaWc5N2JCODVjK2xrR0taTUhBR0NDc0dBUVVGQndFQkJHUXdZakF0QmdnckJnRUZCUWN3QW9ZaGFIUjBjRG92TDJObGNuUnpMbUZ3Y0d4bExtTnZiUzkzZDJSeVp6WXVaR1Z5TURFR0NDc0dBUVVGQnpBQmhpVm9kSFJ3T2k4dmIyTnpjQzVoY0hCc1pTNWpiMjB2YjJOemNEQXpMWGQzWkhKbk5qQXlNSUlCSGdZRFZSMGdCSUlCRlRDQ0FSRXdnZ0VOQmdvcWhraUc5Mk5rQlFZQk1JSCtNSUhEQmdnckJnRUZCUWNDQWpDQnRneUJzMUpsYkdsaGJtTmxJRzl1SUhSb2FYTWdZMlZ5ZEdsbWFXTmhkR1VnWW5rZ1lXNTVJSEJoY25SNUlHRnpjM1Z0WlhNZ1lXTmpaWEIwWVc1alpTQnZaaUIwYUdVZ2RHaGxiaUJoY0hCc2FXTmhZbXhsSUhOMFlXNWtZWEprSUhSbGNtMXpJR0Z1WkNCamIyNWthWFJwYjI1eklHOW1JSFZ6WlN3Z1kyVnlkR2xtYVdOaGRHVWdjRzlzYVdONUlHRnVaQ0JqWlhKMGFXWnBZMkYwYVc5dUlIQnlZV04wYVdObElITjBZWFJsYldWdWRITXVNRFlHQ0NzR0FRVUZCd0lCRmlwb2RIUndPaTh2ZDNkM0xtRndjR3hsTG1OdmJTOWpaWEowYVdacFkyRjBaV0YxZEdodmNtbDBlUzh3SFFZRFZSME9CQllFRklGaW9HNHdNTVZBMWt1OXpKbUdOUEFWbjNlcU1BNEdBMVVkRHdFQi93UUVBd0lIZ0RBUUJnb3Foa2lHOTJOa0Jnc0JCQUlGQURBS0JnZ3Foa2pPUFFRREF3TnBBREJtQWpFQStxWG5SRUM3aFhJV1ZMc0x4em5qUnBJelBmN1ZIejlWL0NUbTgrTEpsclFlcG5tY1B2R0xOY1g2WFBubGNnTEFBakVBNUlqTlpLZ2c1cFE3OWtuRjRJYlRYZEt2OHZ1dElETVhEbWpQVlQzZEd2RnRzR1J3WE95d1Iya1pDZFNyZmVvdCIsIk1JSURGakNDQXB5Z0F3SUJBZ0lVSXNHaFJ3cDBjMm52VTRZU3ljYWZQVGp6Yk5jd0NnWUlLb1pJemowRUF3TXdaekViTUJrR0ExVUVBd3dTUVhCd2JHVWdVbTl2ZENCRFFTQXRJRWN6TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd0hoY05NakV3TXpFM01qQXpOekV3V2hjTk16WXdNekU1TURBd01EQXdXakIxTVVRd1FnWURWUVFERER0QmNIQnNaU0JYYjNKc1pIZHBaR1VnUkdWMlpXeHZjR1Z5SUZKbGJHRjBhVzl1Y3lCRFpYSjBhV1pwWTJGMGFXOXVJRUYxZEdodmNtbDBlVEVMTUFrR0ExVUVDd3dDUnpZeEV6QVJCZ05WQkFvTUNrRndjR3hsSUVsdVl5NHhDekFKQmdOVkJBWVRBbFZUTUhZd0VBWUhLb1pJemowQ0FRWUZLNEVFQUNJRFlnQUVic1FLQzk0UHJsV21aWG5YZ3R4emRWSkw4VDBTR1luZ0RSR3BuZ24zTjZQVDhKTUViN0ZEaTRiQm1QaENuWjMvc3E2UEYvY0djS1hXc0w1dk90ZVJoeUo0NXgzQVNQN2NPQithYW85MGZjcHhTdi9FWkZibmlBYk5nWkdoSWhwSW80SDZNSUgzTUJJR0ExVWRFd0VCL3dRSU1BWUJBZjhDQVFBd0h3WURWUjBqQkJnd0ZvQVV1N0Rlb1ZnemlKcWtpcG5ldnIzcnI5ckxKS3N3UmdZSUt3WUJCUVVIQVFFRU9qQTRNRFlHQ0NzR0FRVUZCekFCaGlwb2RIUndPaTh2YjJOemNDNWhjSEJzWlM1amIyMHZiMk56Y0RBekxXRndjR3hsY205dmRHTmhaek13TndZRFZSMGZCREF3TGpBc29DcWdLSVltYUhSMGNEb3ZMMk55YkM1aGNIQnNaUzVqYjIwdllYQndiR1Z5YjI5MFkyRm5NeTVqY213d0hRWURWUjBPQkJZRUZEOHZsQ05SMDFESm1pZzk3YkI4NWMrbGtHS1pNQTRHQTFVZER3RUIvd1FFQXdJQkJqQVFCZ29xaGtpRzkyTmtCZ0lCQkFJRkFEQUtCZ2dxaGtqT1BRUURBd05vQURCbEFqQkFYaFNxNUl5S29nTUNQdHc0OTBCYUI2NzdDYUVHSlh1ZlFCL0VxWkdkNkNTamlDdE9udU1UYlhWWG14eGN4ZmtDTVFEVFNQeGFyWlh2TnJreFUzVGtVTUkzM3l6dkZWVlJUNHd4V0pDOTk0T3NkY1o0K1JHTnNZRHlSNWdtZHIwbkRHZz0iLCJNSUlDUXpDQ0FjbWdBd0lCQWdJSUxjWDhpTkxGUzVVd0NnWUlLb1pJemowRUF3TXdaekViTUJrR0ExVUVBd3dTUVhCd2JHVWdVbTl2ZENCRFFTQXRJRWN6TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd0hoY05NVFF3TkRNd01UZ3hPVEEyV2hjTk16a3dORE13TVRneE9UQTJXakJuTVJzd0dRWURWUVFEREJKQmNIQnNaU0JTYjI5MElFTkJJQzBnUnpNeEpqQWtCZ05WQkFzTUhVRndjR3hsSUVObGNuUnBabWxqWVhScGIyNGdRWFYwYUc5eWFYUjVNUk13RVFZRFZRUUtEQXBCY0hCc1pTQkpibU11TVFzd0NRWURWUVFHRXdKVlV6QjJNQkFHQnlxR1NNNDlBZ0VHQlN1QkJBQWlBMklBQkpqcEx6MUFjcVR0a3lKeWdSTWMzUkNWOGNXalRuSGNGQmJaRHVXbUJTcDNaSHRmVGpqVHV4eEV0WC8xSDdZeVlsM0o2WVJiVHpCUEVWb0EvVmhZREtYMUR5eE5CMGNUZGRxWGw1ZHZNVnp0SzUxN0lEdll1VlRaWHBta09sRUtNYU5DTUVBd0hRWURWUjBPQkJZRUZMdXczcUZZTTRpYXBJcVozcjY5NjYvYXl5U3JNQThHQTFVZEV3RUIvd1FGTUFNQkFmOHdEZ1lEVlIwUEFRSC9CQVFEQWdFR01Bb0dDQ3FHU000OUJBTURBMmdBTUdVQ01RQ0Q2Y0hFRmw0YVhUUVkyZTN2OUd3T0FFWkx1Tit5UmhIRkQvM21lb3locG12T3dnUFVuUFdUeG5TNGF0K3FJeFVDTUcxbWloREsxQTNVVDgyTlF6NjBpbU9sTTI3amJkb1h0MlFmeUZNbStZaGlkRGtMRjF2TFVhZ002QmdENTZLeUtBPT0iXX0.eyJyZWNlaXB0VHlwZSI6IlByb2R1Y3Rpb24iLCJhcHBBcHBsZUlkIjoxNjAwNTI1MDYxLCJidW5kbGVJZCI6ImNvbS5sb2NrZXQuTG9ja2V0IiwiYXBwbGljYXRpb25WZXJzaW9uIjoiMTUzMyIsInZlcnNpb25FeHRlcm5hbElkZW50aWZpZXIiOjg5MDI1MTIxMywicmVjZWlwdENyZWF0aW9uRGF0ZSI6MTc4Nzg1MjUxMTQxMywicmVxdWVzdERhdGUiOjE3ODc4NTI1MTE0MTMsIm9yaWdpbmFsUHVyY2hhc2VEYXRlIjoxNjk1NzE2NjU3MTM1LCJvcmlnaW5hbEFwcGxpY2F0aW9uVmVyc2lvbiI6IjEiLCJkZXZpY2VWZXJpZmljYXRpb24iOiJjUWdUekRBV29QRmF1ZmhkOXpBK2RHM2ozbnlNQ2QwakIyTk01MDZjMXlYS0VQNzNWbGdqYk1ESitRVGtQcm44IiwiZGV2aWNlVmVyaWZpY2F0aW9uTm9uY2UiOiI0MmI2NGE3ZS0xZTUyLTQyZDUtOWNjYi02MmU5MjY2NTgxZmUiLCJvcmlnaW5hbFBsYXRmb3JtIjoiaU9TIiwiYXBwVHJhbnNhY3Rpb25JZCI6IjcwNTI4Njk1Mzg1ODM2NDc0NyJ9.IBGcHGb3Tyugggz1V_21N5eEM-mq4ED7QwmNV6cIgkK-XIu2ahTI1xgVEpEnqcjnGR-xDpWhcZ---CVUkqk_iA0",
        "hash_params": "app_user_id,fetch_token,app_transaction:sha256:cb2c9fdcfa40a8ea122e6ea8c420d50be8b69f45ea51a5a694983928c627d5f1",
        "hash_headers": "X-Is-Sandbox:sha256:b5bea41b6c623f7c09f1bf24dcae58ebab3c0cdd90ad966bc43a45b44867e12b",
        "is_sandbox": "true",
    }
]

# ==========================================
# CẤU HÌNH HEADER TỪ TOOL TELEGRAM
# ==========================================
REVENUECAT_HEADERS = {
    'Host': 'api.revenuecat.com',
    'Authorization': 'Bearer appl_JngFETzdodyLmCREOlwTUtXdQik',
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'X-Platform': 'iOS',
    'X-Platform-Version': 'Version 26.2 (Build 23C55)',
    'X-Platform-Device': 'iPhone15,3',
    'X-Platform-Flavor': 'native',
    'X-Version': '5.41.0',
    'X-Client-Version': '2.32.2',
    'X-Client-Bundle-ID': 'com.locket.Locket',
    'X-Client-Build-Version': '3',
    'X-StoreKit2-Enabled': 'true',
    'X-StoreKit-Version': '2',
    'X-Observer-Mode-Enabled': 'false',
    'X-Is-Sandbox': 'true',
    'X-Storefront': 'VNM',
    'X-Apple-Device-Identifier': '39A73C25-1E05-4350-ADA7-5CD3FE1079E8',
    'X-Preferred-Locales': 'vi_KR,ko_KR,en_KR',
    'X-Nonce': 'w0Mlb6+AmV4WYuVv',
    'X-Is-Backgrounded': 'false',
    'X-Retry-Count': '0',
    'X-Is-Debug-Build': 'false',
    'User-Agent': 'Locket/3 CFNetwork/3860.300.31 Darwin/25.2.0',
    'Accept-Language': 'vi-VN,vi;q=0.9',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'X-RevenueCat-ETag': ''
}

class LocketAPI:
    def __init__(self, token=None):
        pass

    def getUserByUsername(self, username):
        """
        Cào UID chuẩn xác 100% bằng thuật toán của tool Telegram.
        """
        if not username:
            raise ValueError("Username is required")

        url = f"https://locket.cam/{username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
            "Accept": "text/html"
        }
        
        try:
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
            html_text = response.text
            redirect_url = str(response.url)

            uid = None
            
            # 1. Tìm trực tiếp
            m = re.search(r'/invites/([A-Za-z0-9]{28})', html_text)
            if m:
                uid = m.group(1)
                
            # 2. Tìm bên trong tham số mã hóa (Quan trọng nhất)
            if not uid:
                lp = re.search(r'link=([^\s"\'>]+)', html_text)
                if lp:
                    try:
                        d = lp.group(1).replace('%3A', ':').replace('%2F', '/')
                        dm = re.search(r'/invites/([A-Za-z0-9]{28})', d)
                        if dm: 
                            uid = dm.group(1)
                    except:
                        pass
                        
            # 3. Tìm từ URL chuyển hướng
            if not uid:
                m_redir = re.search(r'/invites/([A-Za-z0-9]{28})', redirect_url)
                if m_redir:
                    uid = m_redir.group(1)

            if uid:
                return {
                    "result": {
                        "data": {
                            "uid": uid,
                            "username": username,
                            "first_name": "", 
                            "last_name": f"@{username}",
                            "profile_picture_url": "" 
                        }
                    }
                }
            else:
                raise Exception("Không tìm thấy User.")
                
        except Exception as e:
            raise Exception(f"Lỗi khi tìm User: {str(e)}")

    def restorePurchase(self, uid):
        url = "https://api.revenuecat.com/v1/receipts"
        token_config = TOKEN_SETS[0]
        
        body = {
            "product_id": "locket_199_1m", 
            "fetch_token": token_config['fetch_token'], 
            "app_transaction": token_config['app_transaction'],
            "app_user_id": uid, 
            "is_restore": True, 
            "store_country": "VNM", 
            "currency": "USD",
            "price": "1.99", 
            "normal_duration": "P1M", 
            "subscription_group_id": "21419447",
            "observer_mode": False, 
            "initiation_source": "restore", 
            "offers": [],
            "attributes": { 
                "$attConsentStatus": { "updated_at_ms": int(time.time() * 1000), "value": "notDetermined" } 
            }
        }
        
        current_headers = REVENUECAT_HEADERS.copy()
        payload_str = json.dumps(body)
        current_headers['Content-Length'] = str(len(payload_str))
        
        if token_config.get('hash_params'):
            current_headers['X-Post-Params-Hash'] = token_config['hash_params']
        if token_config.get('hash_headers'):
            current_headers['X-Headers-Hash'] = token_config['hash_headers']
            
        current_headers['X-Is-Sandbox'] = str(token_config['is_sandbox']).lower()

        for attempt in range(3):
            try:
                response = requests.post(url, headers=current_headers, json=body, timeout=15)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 529:
                    time.sleep(2)
                    continue
                else:
                    try:
                        err_msg = response.json().get('message', str(response.status_code))
                    except:
                        err_msg = str(response.status_code)
                    raise Exception(f"Bị từ chối: {err_msg}")
                    
            except Exception as e:
                if attempt == 2:
                    raise Exception(f"Lỗi mạng: {str(e)}")
                time.sleep(2)
                
        raise Exception("Timeout / Thất bại sau nhiều lần thử lại")