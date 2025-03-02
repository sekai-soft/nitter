# SPDX-License-Identifier: AGPL-3.0-only
import tables, macros, strutils
import karax/[karaxdsl, vdom]

import renderutils
import ../types, ../prefs_impl

from os import getEnv, existsEnv

macro renderPrefs*(): untyped =
  result = nnkCall.newTree(
    ident("buildHtml"), ident("tdiv"), nnkStmtList.newTree())

  for header, options in prefList:
    result[2].add nnkCall.newTree(
      ident("legend"),
      nnkStmtList.newTree(
        nnkCommand.newTree(ident("text"), newLit(header))))

    for pref in options:
      let procName = ident("gen" & capitalizeAscii($pref.kind))
      let state = nnkDotExpr.newTree(ident("prefs"), ident(pref.name))
      var stmt = nnkStmtList.newTree(
        nnkCall.newTree(procName, newLit(pref.name), newLit(pref.label), state))

      case pref.kind
      of checkbox: discard
      of input: stmt[0].add newLit(pref.placeholder)
      of select:
        if pref.name == "theme":
          stmt[0].add ident("themes")
        else:
          stmt[0].add newLit(pref.options)

      result[2].add stmt

let openNitterRssUrlJs = """
javascript:(function() {
  const url = window.location.href;
  if (!url.startsWith("https://x.com")) {
    alert("This is not a Twitter page");
    return
  }
  const rssUrl = `HTTP_OR_S://HOSTNAME${url.slice("https://x.com".length)}/rssRSS_KEY`;
  window.open(rssUrl, '_blank').focus();
})();
"""

let subscribeNitterRssToMinifluxJs = """
javascript:(function() {
  const url = window.location.href;
  if (!url.startsWith("https://x.com")) {
    alert("This is not a Twitter page");
    return
  }
  const rssUrl = `HTTP_OR_S://HOSTNAME${url.slice("https://x.com".length)}/rssRSS_KEY`;
  const minifluxUrl = `https://MINIFLUX_HOSTNAME/bookmarklet?uri=${encodeURIComponent(rssUrl)}`;
  window.open(minifluxUrl, '_blank').focus();
})();
"""

let subscribeNitterRssToInoreaderJs = """
javascript:(function() {
  const url = window.location.href;
  if (!url.startsWith("https://x.com")) {
    alert("This is not a Twitter page");
    return
  }
  const rssUrl = `HTTP_OR_S://HOSTNAME${url.slice("https://x.com".length)}/rssRSS_KEY`;
  const inoreaderUrl = `https://www.inoreader.com/search/feeds/${encodeURIComponent(rssUrl)}`;
  window.open(inoreaderUrl, '_blank').focus();
})();
"""

proc renderPreferences*(prefs: Prefs; path: string; themes: seq[string]; hostname: string; useHttps: bool): VNode =
  buildHtml(tdiv(class="overlay-panel")):
    fieldset(class="preferences"):
      form(`method`="post", action="/saveprefs", autocomplete="off"):
        refererField path

        renderPrefs()

        legend:
          text "Bookmarklets (drag them to bookmark bar)"

        if prefs.minifluxHostname.len > 0:
          a(href=subscribeNitterRssToMinifluxJs
            .replace("MINIFLUX_HOSTNAME", prefs.minifluxHostname)
            .replace("HTTP_OR_S", if useHttps: "https" else: "http")
            .replace("HOSTNAME", hostname)
            .replace("RSS_KEY", if existsEnv("INSTANCE_RSS_PASSWORD"): "?key=" & getEnv("INSTANCE_RSS_PASSWORD") else: "")):
            text "Subscribe Nitter RSS to Miniflux"

          br()

        a(href=subscribeNitterRssToInoreaderJs
          .replace("HTTP_OR_S", if useHttps: "https" else: "http")
          .replace("HOSTNAME", hostname)
          .replace("RSS_KEY", if existsEnv("INSTANCE_RSS_PASSWORD"): "?key=" & getEnv("INSTANCE_RSS_PASSWORD") else: "")):
          text "Subscribe Nitter RSS to Inoreader"

        br()

        a(href=openNitterRssUrlJs
          .replace("HTTP_OR_S", if useHttps: "https" else: "http")
          .replace("HOSTNAME", hostname)
          .replace("RSS_KEY", if existsEnv("INSTANCE_RSS_PASSWORD"): "?key=" & getEnv("INSTANCE_RSS_PASSWORD") else: "")):
          text "Open Nitter RSS URL"

        h4(class="note"):
          text "Preferences are stored client-side using cookies without any personal information."

        button(`type`="submit", class="pref-submit"):
          text "Save preferences"

      buttonReferer "/resetprefs", "Reset preferences", path, class="pref-reset"
