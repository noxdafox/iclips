define(["codemirror/lib/codemirror",
        "codemirror/addon/mode/simple"],
       function(){

           var onload = function(){
               console.log("Loading CLIPS Kernel..")

               CodeMirror.defineSimpleMode("clips", {
                   start: [
                       {regex: /deffunction|deftemplate|defrule|defclass|defmodule|defglobal|deffacts|slot|if|for|while|else|is-a|multislot|eq|neq/,
                        token: "keyword"},
                       {regex: /STRING|SYMBOL|INTEGER|FLOAT/, token: "keyword"},
                       {regex: /TRUE|FALSE|nil|crlf| t /, token: "atom"},
                       {regex: /\?[a-zA-Z0-9\-]*/, token: "var"},
                       {regex: /"(?:[^\\]|\\.)*?(?:"|$)/, token: "string"},
                       {regex: /;.*/, token: "comment"},
                       {regex: /(\()([a-zA-Z0-9\-\$]+)/, token: [null, "function"], indent: true},
                       {regex: /[-+\/*=<>&:$]+/, token: "operator"},
                       {regex: /[\(]/, indent: true},
                       {regex: /[\)]/, dedent: true},
                   ],
                   meta: {
                       dontIndentStates: ["comment"],
                       lineComment: ";"
                   }
               });

               console.log("CLIPS Kernel successfully loaded.")
           }

           return {onload:onload}
       })
