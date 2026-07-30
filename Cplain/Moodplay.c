#include <windows.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

HWND hInput, hButton, hResult, hWnd;
char g_resp[16384];

DWORD WINAPI Fetch(LPVOID p) {
    char* mood = (char*)p;
    char json[1024];
    
    // Using the structural /api/chat format to enforce strict system control rules over Gemma 3
    snprintf(json, sizeof(json),
        "{\"model\":\"gemma3\",\"messages\":["
        "{\"role\":\"system\",\"content\":\"You are a playlist generator.Output ONLY a raw numbered list of 5 songs with their descriptions. Never include intro sentences, greetings, or sign-offs.\"},"
        "{\"role\":\"user\",\"content\":\"List 5 songs for someone feeling %s.\"}"
        "],\"stream\":false}", mood);
    
    CreateDirectoryA("C:\\Temp", NULL);
    FILE* f = fopen("C:\\Temp\\mp.json", "w");
    if (f) { fprintf(f, "%s", json); fclose(f); }

    SHELLEXECUTEINFOA sei = {0};
    sei.cbSize = sizeof(sei);
    sei.fMask  = SEE_MASK_NOCLOSEPROCESS;
    sei.lpVerb = "open";
    sei.lpFile = "curl";
    sei.lpParameters = "-s -X POST http://localhost:11434/api/chat "
                       "-H \"Content-Type: application/json\" "
                       "--data-binary @C:\\Temp\\mp.json -o C:\\Temp\\mp.txt";
    sei.nShow  = SW_HIDE;
    ShellExecuteExA(&sei);
    if (sei.hProcess) { WaitForSingleObject(sei.hProcess, 60000); CloseHandle(sei.hProcess); }

    FILE* fp = fopen("C:\\Temp\\mp.txt", "r");
    char raw[16384] = {0};
    if (fp) { fread(raw, 1, sizeof(raw) - 1, fp); fclose(fp); }

    // Chat API returns "content":"text" block
    char* s = strstr(raw, "\"content\":\"");
    int i = 0;
    if (s) {
        s += 11;
        while (*s && i < (int)sizeof(g_resp) - 10) {
            if (*s == '*') { s++; continue; } // Strip markdown formatting
            
            // Un-skippable rule: Force double spacing right before ANY song list number item
            if (*s >= '1' && *s <= '5' && *(s + 1) == '.') {
                if (i > 0) {
                    g_resp[i++] = '\r'; g_resp[i++] = '\n';
                    g_resp[i++] = '\r'; g_resp[i++] = '\n';
                }
            }

            // Translate JSON escaped newlines cleanly to Windows breaks
            if (*s == '\\') {
                s++;
                if (*s == 'n') {
                    g_resp[i++] = '\r'; g_resp[i++] = '\n';
                } else if (*s == '"')  g_resp[i++] = '"';
                  else if (*s == '\\') g_resp[i++] = '\\';
            } else if (*s == '"') {
                // Check if this quote terminates the message content string
                if (*(s + 1) == ',' || *(s + 1) == '}') break;
                g_resp[i++] = '"';
            } else {
                g_resp[i++] = *s;
            }
            s++;
        }
    } else {
        strcpy(g_resp, "Could not connect to Ollama.\r\nRun: ollama serve");
        i = strlen(g_resp);
    }
    g_resp[i] = '\0';

    PostMessage(hWnd, WM_USER + 1, 0, 0);
    free(mood);
    return 0;
}

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp) {
    switch(msg) {
    case WM_CREATE: {
        HFONT fn = CreateFontW(17,0,0,0,FW_NORMAL,0,0,0,0,0,0,CLEARTYPE_QUALITY,0,L"Segoe UI");
        HFONT fb = CreateFontW(32,0,0,0,FW_BOLD,0,0,0,0,0,0,CLEARTYPE_QUALITY,0,L"Segoe UI");
        HWND t = CreateWindowW(L"STATIC", L"MoodPlay", WS_CHILD | WS_VISIBLE, 30, 16, 300, 40, hwnd, 0, 0, 0);
        SendMessage(t, WM_SETFONT, (WPARAM)fb, 1);
        HWND l = CreateWindowW(L"STATIC", L"How are you feeling?", WS_CHILD | WS_VISIBLE, 30, 72, 400, 22, hwnd, 0, 0, 0);
        SendMessage(l, WM_SETFONT, (WPARAM)fn, 1);
        hInput = CreateWindowW(L"EDIT", L"", WS_CHILD | WS_VISIBLE | WS_BORDER | ES_AUTOHSCROLL, 30, 100, 520, 36, hwnd, (HMENU)1, 0, 0);
        SendMessage(hInput, WM_SETFONT, (WPARAM)fn, 1);
        hButton = CreateWindowW(L"BUTTON", L"Find Playlist", WS_CHILD | WS_VISIBLE, 562, 100, 148, 36, hwnd, (HMENU)2, 0, 0);
        SendMessage(hButton, WM_SETFONT, (WPARAM)fn, 1);
        hResult = CreateWindowW(L"EDIT", L"Enter mood and click Find Playlist!",
            WS_CHILD | WS_VISIBLE | WS_BORDER | WS_VSCROLL | ES_MULTILINE | ES_READONLY | ES_AUTOVSCROLL,
            30, 154, 680, 480, hwnd, (HMENU)3, 0, 0);
        SendMessage(hResult, WM_SETFONT, (WPARAM)fn, 1);
        return 0;
    }
    case WM_CTLCOLORSTATIC:
        SetTextColor((HDC)wp, RGB(212, 83, 126)); SetBkColor((HDC)wp, RGB(18, 18, 28));
        return (LRESULT)CreateSolidBrush(RGB(18, 18, 28));
    case WM_CTLCOLOREDIT:
        if ((HWND)lp == hResult) { 
            SetTextColor((HDC)wp, RGB(230, 225, 250)); SetBkColor((HDC)wp, RGB(22, 22, 34)); 
            return (LRESULT)CreateSolidBrush(RGB(22, 22, 34)); 
        }
        SetTextColor((HDC)wp, RGB(240, 237, 245)); SetBkColor((HDC)wp, RGB(30, 30, 42));
        return (LRESULT)CreateSolidBrush(RGB(30, 30, 42));
    case WM_CTLCOLORBTN:
        SetTextColor((HDC)wp, RGB(255, 255, 255)); SetBkColor((HDC)wp, RGB(212, 83, 126));
        return (LRESULT)CreateSolidBrush(RGB(212, 83, 126));
    case WM_ERASEBKGND: {
        RECT rc; GetClientRect(hwnd, &rc);
        HBRUSH br = CreateSolidBrush(RGB(18, 18, 28)); FillRect((HDC)wp, &rc, br); DeleteObject(br);
        return 1;
    }
    case WM_PAINT: {
        PAINTSTRUCT ps; HDC hdc = BeginPaint(hwnd, &ps); SetBkMode(hdc, TRANSPARENT);
        HPEN pen = CreatePen(PS_SOLID, 1, RGB(212, 83, 126)); HPEN old = (HPEN)SelectObject(hdc, pen);
        MoveToEx(hdc, 30, 64, NULL); LineTo(hdc, 720, 64);
        SelectObject(hdc, old); DeleteObject(pen); EndPaint(hwnd, &ps); return 0;
    }
    case WM_COMMAND:
        if (LOWORD(wp) == 2) {
            WCHAR wm[256]; GetWindowTextW(hInput, wm, 256);
            if (!wcslen(wm)) return 0;
            EnableWindow(hButton, FALSE);
            SetWindowTextW(hResult, L"Finding your playlist... please wait.");
            char* mood = (char*)malloc(256);
            WideCharToMultiByte(CP_UTF8, 0, wm, -1, mood, 256, NULL, NULL);
            CreateThread(NULL, 0, Fetch, mood, 0, NULL);
        }
        return 0;
    case WM_USER + 1: {
        WCHAR wr[16384]; MultiByteToWideChar(CP_UTF8, 0, g_resp, -1, wr, 16384);
        SetWindowTextW(hResult, wr); EnableWindow(hButton, TRUE);
        return 0;
    }
    case WM_DESTROY: PostQuitMessage(0); return 0;
    }
    return DefWindowProc(hwnd, msg, wp, lp);
}

int WINAPI WinMain(HINSTANCE hi, HINSTANCE h, LPSTR s, int n) {
    WNDCLASSW wc = {0};
    wc.lpfnWndProc = WndProc; wc.hInstance = hi; wc.lpszClassName = L"MoodPlay";
    wc.hbrBackground = (HBRUSH)GetStockObject(BLACK_BRUSH); wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    RegisterClassW(&wc);
    hWnd = CreateWindowW(L"MoodPlay", L"MoodPlay", WS_OVERLAPPEDWINDOW & ~WS_MAXIMIZEBOX & ~WS_THICKFRAME,
        CW_USEDEFAULT, CW_USEDEFAULT, 760, 700, NULL, NULL, hi, NULL);
    ShowWindow(hWnd, n); UpdateWindow(hWnd);
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) { TranslateMessage(&msg); DispatchMessage(&msg); }
    return (int)msg.wParam;
}