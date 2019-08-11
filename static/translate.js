(function() {
    "use strict";

    function Translator(translations, lang) {
        var language = lang || window.navigator.language.split("-")[0];

        function translate(s) {
            return (translations[language] || {})[s] || s;
        }

        return translate;
    }

    window.Translator = Translator;
})();
// vim: set ts=4 sw=4 et:
