import tables, macros, strutils, os
import karax/[karaxdsl, vdom, vstyles]

import renderutils
import ../types, ../prefs_impl

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

proc renderPreferences*(prefs: Prefs; path: string; themes: seq[string]): VNode =
  buildHtml(tdiv(class="overlay-panel")):
    fieldset(class="preferences"):
      form(`method`="post", action="/saveprefs"):
        refererField path

        renderPrefs()

        button(`type`="submit", class="pref-submit"):
          text "Save preferences"

      buttonReferer "/resetprefs", "Reset Preferences", path, class="pref-reset"
