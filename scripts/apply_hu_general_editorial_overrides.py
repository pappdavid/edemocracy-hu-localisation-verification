#!/usr/bin/env python3
"""Apply human-edited Hungarian wording to the shared public interface locale."""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
EN_PATH = ROOT / "config/locales/en/general.yml"
HU_PATH = ROOT / "config/locales/hu-HU/general.yml"
CHANGELOG = ROOT / "docs/hungarian_localisation_editorial_manual_changes.tsv"

OVERRIDES = {
    "account.show.last_sign_in": "Utolsó bejelentkezés: %{last_sign_in_at}; IP-cím: %{last_sign_in_ip}",
    "account.show.change_credentials_link": "Bejelentkezési adatok módosítása",
    "account.show.erase_account_link": "Fiókom törlése",
    "account.show.finish_verification": "Ellenőrzés folytatása",
    "account.show.public_interests_my_title_list": "Az Ön által követett elemek címkéi",
    "account.show.public_interests_user_title_list": "A felhasználó által követett elemek címkéi",
    "account.show.title": "Saját fiók",
    "account.show.user_permission_info": "Fiókjával a következőket teheti:",
    "account.show.user_permission_verify": "Az összes funkció eléréséhez ellenőrizze fiókját.",
    "account.show.verified_account": "Ellenőrzött fiók",
    "application.close": "Bezárás",
    "comments.actions.confirm_delete": "Biztosan törli ezt a hozzászólást? A művelet nem vonható vissza.",
    "comments.actions.delete": "Hozzászólás törlése",
    "comments.comments_closed": "A hozzászólások lezárultak.",
    "comments.comment.deleted": "Ezt a hozzászólást törölték.",
    "comments.comment.responses.other": "%{count} válasz",
    "comments.comment.responses_show.one": "1 válasz megjelenítése",
    "comments.comment.responses_show.other": "%{count} válasz megjelenítése",
    "comments.comment.responses_collapse.one": "1 válasz elrejtése",
    "comments.comment.responses_collapse.other": "%{count} válasz elrejtése",
    "comments.comment.votes.other": "%{count} szavazat",
    "comments.form.leave_comment": "Írjon hozzászólást",
    "comments.orders.most_voted": "Legtöbb szavazat",
    "comments.orders.oldest": "Legrégebbi elöl",
    "comments.orders.most_commented": "Legtöbb hozzászólás",
    "comments.show.return_to_commentable": "Vissza a tartalomhoz",
    "comments_helper.comment_button": "Hozzászólás közzététele",
    "comments_helper.comment_link": "Hozzászólás",
    "comments_helper.comments_title": "Hozzászólások",
    "debates.debate.votes.other": "%{count} szavazat",
    "debates.form.tags_instructions": "Címkézze fel ezt a vitát.",
    "debates.index.orders.confidence_score": "Legmagasabb értékelés",
    "debates.index.orders.relevance": "Legrelevánsabb",
    "debates.index.orders.recommendations": "Ajánlott",
    "debates.index.recommendations.without_results": "Nincsenek az érdeklődési köréhez kapcsolódó viták.",
    "debates.index.recommendations.without_interests": "Kövesse az Önt érdeklő javaslatokat, hogy személyre szabott ajánlásokat adhassunk.",
    "debates.index.section_header.icon_alt": "Viták ikon",
    "debates.index.section_header.help": "Segítség a vitákhoz",
    "debates.index.section_footer.title": "Segítség a vitákhoz",
    "debates.index.section_footer.help_text_1": "A viták felületén bárki megoszthatja a települést érintő kérdésekkel kapcsolatos véleményét.",
    "debates.index.section_footer.help_text_2": "Új vita indításához regisztrálnia kell az %{org} oldalon. A nyílt vitákhoz hozzászólhat, és az „egyetértek” vagy „nem értek egyet” gombbal értékelheti a bejegyzéseket.",
    "debates.new.recommendation_four": "Használja szabadon ezt a felületet, és hallgassa meg mások véleményét is. Ez a tér Önnek is szól.",
    "debates.new.recommendation_three": "A tárgyszerű kritikát szívesen fogadjuk. Kérjük, maradjon tiszteletteljes és építő jellegű.",
    "debates.show.comments_title": "Hozzászólások",
    "debates.show.share": "Megosztás",
    "form.accept_terms": "Elfogadom a(z) %{policy} és a(z) %{conditions} dokumentumot.",
    "form.errors": "hiba",
    "form.not_saved": "megakadályozta a(z) %{resource} mentését.<br>Kérjük, ellenőrizze a megjelölt mezőket.",
    "proposals.create.form.submit_button": "Javaslat létrehozása",
    "proposals.created.preview_title": "Így fog kinézni javaslata közzététel után",
    "proposals.edit.show_link": "Javaslat megtekintése",
    "proposals.retire_form.warning": "A visszavont javaslat nem jelenik meg a fő listában, de a korábbi támogatások megmaradnak. A javaslat oldalán tájékoztatás jelenik meg arról, hogy a szerző már nem kéri további támogatását.",
    "proposals.retire_options.duplicated": "Duplikált",
    "proposals.form.tags_instructions": "Címkézze fel ezt a javaslatot. Választhat a javasolt kategóriák közül, vagy saját címkét is hozzáadhat.",
    "proposals.form.proposal_video_url_note": "YouTube- vagy Vimeo-hivatkozást is hozzáadhat.",
    "proposals.index.orders.confidence_score": "Legmagasabb értékelés",
    "proposals.index.orders.most_commented": "Legtöbb hozzászólás",
    "proposals.index.orders.relevance": "Legrelevánsabb",
    "proposals.index.orders.recommendations": "Ajánlott",
    "proposals.index.recommendations.without_results": "Nincsenek az érdeklődési köréhez kapcsolódó javaslatok.",
    "proposals.index.recommendations.without_interests": "Kövesse az Önt érdeklő javaslatokat, hogy személyre szabott ajánlásokat adhassunk.",
    "proposals.index.selected_proposals": "Kiválasztott javaslatok",
    "proposals.index.selected_proposals_link": "Kiválasztott javaslatok megtekintése",
    "proposals.index.search_form.placeholder": "Javaslatok keresése…",
    "proposals.index.select_order_long": "Javaslatok rendezése:",
    "proposals.index.start_proposal": "Javaslat létrehozása",
    "proposals.index.section_header.icon_alt": "Javaslatok ikon",
    "proposals.index.section_header.help": "Segítség a javaslatokhoz",
    "proposals.index.section_footer.title": "Segítség a javaslatokhoz",
    "proposals.index.section_footer.description": "A polgári javaslatok segítségével a lakosok és közösségek kezdeményezéseket nyújthatnak be. A kellő támogatást elérő javaslatok a helyi szabályok szerinti további eljárásba kerülhetnek.",
    "proposals.new.form.submit_button": "Javaslat létrehozása",
    "proposals.new.recommendation_three": "Használja szabadon ezt a felületet, és hallgassa meg mások véleményét is. Ez a tér Önnek is szól.",
    "proposals.new.recommendations_title": "Útmutató javaslat létrehozásához",
    "proposals.new.start_new": "Új javaslat létrehozása",
    "proposals.proposal.created": "Javaslata elkészült!",
    "proposals.proposal.share.guide": "Most megoszthatja javaslatát, hogy mások is támogathassák.",
    "proposals.proposal.share.view_proposal": "Nem most, javaslatom megtekintése",
    "proposals.proposal.already_supported": "Ön már támogatta ezt a javaslatot. Ossza meg másokkal is!",
    "proposals.proposal.support_label": "%{proposal} támogatása",
    "proposals.proposal.supports.other": "%{count} támogatás",
    "proposals.proposal.votes.other": "%{count} szavazat",
    "proposals.show.comments_tab": "Hozzászólások",
    "proposals.show.dashboard_proposal_link": "Javaslatkezelő felület",
    "proposals.show.share": "Megosztás",
    "proposals.show.embed_video_title": "Videó a(z) %{proposal} javaslathoz",
    "proposals.show.draft": "Ez a javaslat még piszkozat. Nem kaphat támogatást, és nem jelenik meg a javaslatok között.",
    "dashboard.menu.my_proposal": "Javaslatom szerkesztése",
    "dashboard.menu.progress": "Előrehaladás",
    "dashboard.menu.resources": "Erőforrások",
    "dashboard.menu.mailing": "E-mail",
    "dashboard.menu.poster": "Plakát",
    "dashboard.menu.messages": "Üzenetek a követőknek",
    "dashboard.form.request": "Igénylés",
    "dashboard.progress.title": "Előrehaladási diagram",
    "dashboard.progress.supports": "Támogatások",
    "dashboard.index.title": "Javaslatkezelő felület",
    "dashboard.poster.index.title": "Plakát előnézete",
    "dashboard.mailer.forward.subtitle": "Ha támogatja, <br>megvalósíthatjuk.",
    "dashboard.mailer.forward.share_in": "Ossza meg",
    "dashboard.mailer.forward.hi": "Üdvözlöm!",
    "polls.dates": "%{open_at}–%{closed_at}",
    "polls.final_date": "Végleges számlálás és eredmények",
    "polls.form.maximum_exceeded": "%{given} választ jelölt meg, de legfeljebb %{maximum} válasz jelölhető meg.",
    "polls.index.filters.current": "Nyitott",
    "polls.index.geozone_restricted": "Kerületek",
    "polls.index.unverified": "A részvételhez ellenőriznie kell fiókját.",
    "polls.index.cant_answer": "Ez a szavazás az Ön földrajzi területén nem érhető el.",
    "polls.index.section_header.icon_alt": "Szavazás ikon",
    "polls.index.section_footer.description": "A polgári szavazás olyan részvételi forma, amelyben a szavazati joggal rendelkező polgárok közvetlenül dönthetnek a feltett kérdésekről.",
    "polls.show.already_voted_in_booth": "Ön már személyesen részt vett a szavazásban, ezért nem szavazhat újra.",
    "polls.show.already_voted_in_web": "Ön már részt vett ebben a szavazásban. Újabb szavazat leadásával a korábbi választ felülírja.",
    "polls.show.already_voted_blank_in_web": "Ön már üres szavazatot adott le ebben a szavazásban. Újabb szavazat leadásával a korábbi választ felülírja.",
    "polls.show.comments_tab": "Hozzászólások",
    "polls.show.cant_answer_verify": "A válaszadáshoz %{verify_link}.",
    "polls.show.verify_link": "ellenőrizze fiókját",
    "polls.show.cant_answer_wrong_geozone": "Ez a kérdés az Ön földrajzi területén nem érhető el.",
    "polls.show.zoom_plus": "Kép nagyítása",
    "polls.show.read_more": "További információ: %{answer}",
    "polls.show.read_less": "Kevesebb információ: %{answer}",
    "polls.show.stats.total_votes": "Leadott szavazatok száma",
    "polls.show.stats.mail": "LEVÉL",
    "polls.show.stats.booth": "SZAVAZÓHELYISÉG",
    "polls.show.stats.total": "ÖSSZESEN",
    "polls.show.stats.white": "Üres szavazat",
    "polls.show.results.most_voted_answer": "A legtöbb szavazatot kapott válasz:",
    "polls.poll_header.back_to_proposal": "Vissza a javaslathoz",
    "proposal_notifications.new.info_about_receivers": "Ezt az értesítést <strong>%{count} személy</strong> kapja meg, és a(z) %{proposal_page} oldalon is megjelenik.<br>Az értesítéseket nem azonnal küldjük ki: a felhasználók rendszeres e-mailes összefoglalót kapnak a javaslataikról.",
    "proposal_notifications.show.back": "Vissza a tartalomhoz",
    "shared.save": "Mentés",
    "shared.delete": "Törlés",
    "shared.advanced_search.date_placeholder": "ÉÉÉÉ/HH/NN",
    "shared.advanced_search.date_range_blank": "Válasszon dátumot",
    "shared.advanced_search.from": "Ettől",
    "shared.advanced_search.general": "Szöveg szerint",
    "shared.advanced_search.search": "Keresés",
    "shared.advanced_search.to": "Eddig",
    "shared.back": "Vissza",
    "shared.check_all": "Összes kijelölése",
    "shared.check_none": "Kijelölés megszüntetése",
    "shared.follow": "Követés",
    "shared.following": "Követés alatt",
    "shared.followable.proposal.create.notice": "Mostantól követi ezt a polgári javaslatot.<br>Értesítjük a változásokról.",
    "shared.followable.proposal.destroy.notice": "Már nem követi ezt a polgári javaslatot.<br>A továbbiakban nem kap értesítést a változásairól.",
    "shared.show": "Megtekintés",
    "shared.share": "Megosztás",
    "shared.tags_cloud.districts": "Kerületek",
    "shared.tags_cloud.districts_list": "Kerületek listája",
    "shared.you_are_in": "Itt van:",
    "shared.unflag": "Megjelölés visszavonása",
    "shared.translations.languages_in_use.other": "%{count} nyelv használatban",
    "shared.comments.other": "%{count} hozzászólás",
    "social.telegram": "%{org} Telegram",
    "omniauth.facebook.sign_in": "Jelentkezzen be a Facebookkal",
    "omniauth.facebook.sign_up": "Regisztráljon a Facebookkal",
    # Requested by the poll-index view but absent from the upstream English catalogue.
    "polls.index.filter": "Szűrő",
}


def load(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            out.update(flatten(child, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            out.update(flatten(child, f"{prefix}[{index}]"))
    else:
        out[prefix] = value
    return out


def set_path(target: dict[str, Any], path: str, value: Any) -> None:
    current: Any = target
    parts: list[str | int] = []
    for match in re.finditer(r"([^\.\[\]]+)|\[(\d+)\]", path):
        parts.append(int(match.group(2)) if match.group(2) is not None else match.group(1))
    for index, part in enumerate(parts):
        if index == len(parts) - 1:
            current[part] = value
        else:
            next_is_list = isinstance(parts[index + 1], int)
            if part not in current:
                current[part] = [] if next_is_list else {}
            current = current[part]


def main() -> None:
    english = flatten(load(EN_PATH).get("en", {}))
    document = load(HU_PATH)
    hungarian = document.setdefault("hu", {})
    current = flatten(hungarian)
    changes = []
    for key, revised in OVERRIDES.items():
        if key not in english and key != "polls.index.filter":
            raise KeyError(f"Unknown English locale key: {key}")
        previous = current.get(key, "")
        if previous != revised:
            set_path(hungarian, key, revised)
            changes.append(("general.yml", key, previous, revised, english.get(key, "[upstream key omitted]"), "human editorial revision"))
    HU_PATH.write_text(yaml.safe_dump(document, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    header = not CHANGELOG.exists()
    with CHANGELOG.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        if header:
            writer.writerow(["file", "key", "previous_hungarian", "revised_hungarian", "english_source", "method"])
        writer.writerows(changes)
    print(f"Applied {len(changes)} human editorial overrides to general.yml")


if __name__ == "__main__":
    main()
