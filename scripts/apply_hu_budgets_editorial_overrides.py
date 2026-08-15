#!/usr/bin/env python3
"""Apply human-edited Hungarian wording to the participatory-budget journey."""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
EN_PATH = ROOT / "config/locales/en/budgets.yml"
HU_PATH = ROOT / "config/locales/hu-HU/budgets.yml"
CHANGELOG = ROOT / "docs/hungarian_localisation_editorial_manual_changes.tsv"

OVERRIDES = {
    "budgets.ballots.show.title": "Az Ön szavazólapja",
    "budgets.ballots.show.amount_available.knapsack": "Még felhasználható: <span>%{count}</span>",
    "budgets.ballots.show.amount_available.approval.zero": "Még <span>%{count}</span> szavazatot adhat le.",
    "budgets.ballots.show.amount_available.approval.one": "Még <span>%{count}</span> szavazatot adhat le.",
    "budgets.ballots.show.amount_available.approval.other": "Még <span>%{count}</span> szavazatot adhat le.",
    "budgets.ballots.show.amount_spent.approval.zero": "Leadott szavazatok: <span>%{count}</span>",
    "budgets.ballots.show.amount_spent.approval.one": "Leadott szavazatok: <span>%{count}</span>",
    "budgets.ballots.show.amount_spent.approval.other": "Leadott szavazatok: <span>%{count}</span>",
    "budgets.ballots.show.amount_limit.knapsack": "Teljes költségkeret: <span>%{count}</span>",
    "budgets.ballots.show.amount_limit.approval.one": "Legfeljebb <span>1</span> projektre szavazhat.",
    "budgets.ballots.show.amount_limit.approval.other": "Legfeljebb <span>%{count}</span> projektre szavazhat.",
    "budgets.ballots.show.no_balloted_group_yet": "Ebben a kategóriában még nem szavazott. Adja le szavazatát most!",
    "budgets.ballots.show.remove": "Szavazat eltávolítása",
    "budgets.ballots.show.remove_label": "Szavazat eltávolítása: %{investment}",
    "budgets.ballots.show.voted.one": "Ön <span>egy</span> beruházási projektre szavazott.",
    "budgets.ballots.show.voted.other": "Ön <span>%{count}</span> beruházási projektre szavazott.",
    "budgets.ballots.show.voted_info": "Szavazata megerősítést nyert.",
    "budgets.ballots.show.voted_info_2": "Szavazatát a szakasz lezárásáig bármikor módosíthatja.",
    "budgets.ballots.reasons_for_not_balloting.not_verified": "Beruházási projektekre csak ellenőrzött felhasználók szavazhatnak; %{verify_account}.",
    "budgets.ballots.reasons_for_not_balloting.not_selected": "A végső szavazásra ki nem választott beruházási projektek nem támogathatók.",
    "budgets.ballots.reasons_for_not_balloting.not_enough_money": "Már felhasználta a rendelkezésre álló költségkeretet.<br><small>Ne feledje: bármikor %{change_ballot}.</small>",
    "budgets.ballots.reasons_for_not_balloting.no_ballots_allowed": "A kiválasztási szakasz lezárult.",
    "budgets.ballots.reasons_for_not_balloting.different_heading_assigned": "Már egy másik kategóriában szavazott: %{heading_link}.",
    "budgets.ballots.reasons_for_not_balloting.not_enough_available_votes": "Elérte a leadható szavazatok maximális számát.",
    "budgets.ballots.reasons_for_not_balloting.change_ballot": "módosíthatja szavazatait",
    "budgets.ballots.reasons_for_not_balloting.casted_offline": "Ön már személyesen is részt vett a szavazásban.",
    "budgets.groups.show.title": "Válasszon kategóriát",
    "budgets.phase.drafting": "Piszkozat (nyilvánosan nem látható)",
    "budgets.phase.informing": "Tájékoztatás",
    "budgets.phase.reviewing": "Projektek felülvizsgálata",
    "budgets.phase.valuating": "Projektek értékelése",
    "budgets.phase.publishing_prices": "A projektek költségének közzététele",
    "budgets.phase.balloting": "Szavazás a projektekről",
    "budgets.phase.reviewing_ballots": "A szavazás ellenőrzése",
    "budgets.phase.finished": "Lezárt költségvetés",
    "budgets.index.title": "Közösségi költségvetések",
    "budgets.index.section_header.icon_alt": "Közösségi költségvetés ikon",
    "budgets.index.section_header.title": "Közösségi költségvetések",
    "budgets.index.section_header.help": "Segítség a közösségi költségvetéshez",
    "budgets.index.all_phases": "A közösségi költségvetés szakaszai",
    "budgets.index.next_phase": "Következő szakasz",
    "budgets.index.prev_phase": "Előző szakasz",
    "budgets.index.current_phase": "Aktuális szakasz",
    "budgets.index.map": "Beruházási javaslatok a térképen",
    "budgets.index.finished_budgets": "Lezárt közösségi költségvetések",
    "budgets.index.section_footer.title": "Segítség a közösségi költségvetéshez",
    "budgets.index.section_footer.description": "A közösségi költségvetésben a polgárok döntenek arról, hogy a költségvetés egy részét mely projektekre fordítsák.",
    "budgets.investments.form.title": "Beruházási projekt létrehozása",
    "budgets.investments.form.tags_instructions": "Címkézze fel ezt a javaslatot. Választhat a javasolt kategóriák közül, vagy saját címkét is hozzáadhat.",
    "budgets.investments.form.tags_placeholder": "Adja meg a használni kívánt címkéket vesszővel (',') elválasztva.",
    "budgets.investments.index.title": "Közösségi költségvetés",
    "budgets.investments.index.unfeasible": "Nem megvalósítható beruházási projektek",
    "budgets.investments.index.unfeasible_text": "A beruházási projekteknek több feltételnek is meg kell felelniük – jogszerűnek és kellően konkrétnak kell lenniük, valamint nem léphetik túl a költségvetési keretet –, hogy a végső szavazás szakaszába kerüljenek. Azok a projektek, amelyek nem felelnek meg ezeknek a feltételeknek, nem megvalósíthatóként, indoklással együtt jelennek meg az alábbi listában.",
    "budgets.investments.index.by_heading": "Beruházási projektek ebben a kategóriában: %{heading}",
    "budgets.investments.index.search_form.placeholder": "Beruházási projektek keresése…",
    "budgets.investments.index.sidebar.my_ballot": "Az Ön szavazólapja",
    "budgets.investments.index.sidebar.voted_info.knapsack.one": "<strong>Ön egy %{amount_spent} értékű javaslatra szavazott.</strong>",
    "budgets.investments.index.sidebar.voted_info.knapsack.other": "<strong>Ön %{count} javaslatra szavazott, összesen %{amount_spent} értékben.</strong>",
    "budgets.investments.index.sidebar.voted_info.approval.one": "<strong>Ön egy javaslatra szavazott.</strong>",
    "budgets.investments.index.sidebar.voted_info.approval.other": "<strong>Ön %{count} javaslatra szavazott.</strong>",
    "budgets.investments.index.sidebar.change_vote_info.knapsack": "Szavazatát %{phase_end_date}-ig bármikor %{link}. Nem szükséges elköltenie a teljes rendelkezésre álló összeget.",
    "budgets.investments.index.sidebar.change_vote_info.approval": "Szavazatát %{phase_end_date}-ig bármikor %{link}.",
    "budgets.investments.index.sidebar.change_vote_link": "módosíthatja",
    "budgets.investments.index.sidebar.different_heading_assigned": "Másik kategóriában is vannak aktív szavazatai: %{heading_link}.",
    "budgets.investments.index.sidebar.change_ballot": "Ha meggondolja magát, a %{check_ballot} oldalon eltávolíthatja szavazatait, majd újrakezdheti.",
    "budgets.investments.index.sidebar.check_ballot_link": "ellenőrizze szavazatait",
    "budgets.investments.index.sidebar.zero": "Ebben a kategóriában még egyetlen beruházási projektre sem szavazott.",
    "budgets.investments.index.sidebar.verified_only": "Új beruházási projekt létrehozásához %{verify}.",
    "budgets.investments.index.sidebar.create": "Beruházási projekt létrehozása",
    "budgets.investments.index.sidebar.not_logged_in": "Új beruházási projekt létrehozásához %{sign_in} vagy %{sign_up} szükséges.",
    "budgets.investments.index.filter": "Projektek szűrése",
    "budgets.investments.index.filters.unfeasible": "Nem megvalósítható",
    "budgets.investments.index.filters.unselected": "A végső szavazásra ki nem választott",
    "budgets.investments.index.orders.confidence_score": "Legmagasabb értékelés",
    "budgets.investments.share.message": "A(z) %{title} beruházási projektet itt hoztam létre: %{handle}. Hozzon létre Ön is beruházási projektet!",
    "budgets.investments.show.price_explanation": "Az ár magyarázata",
    "budgets.investments.show.code": "Beruházási projekt kódja: <strong>%{code}</strong>",
    "budgets.investments.show.location": "Helyszín: <strong>%{location}</strong>",
    "budgets.investments.show.organization_name": "Javaslattevő szervezet: <strong>%{name}</strong>",
    "budgets.investments.show.share": "Megosztás",
    "budgets.investments.show.supports": "Támogatások",
    "budgets.investments.show.votes": "Szavazatok",
    "budgets.investments.show.project_unfeasible": "Ez a beruházási projekt <strong>nem megvalósítható</strong>, ezért nem kerül a szavazási szakaszba.",
    "budgets.investments.show.project_selected": "Ezt a beruházási projektet <strong>kiválasztották</strong> a szavazási szakaszra.",
    "budgets.investments.show.project_winner": "Nyertes beruházási projekt",
    "budgets.investments.show.project_not_selected": "Ezt a beruházási projektet <strong>nem választották ki</strong> a szavazási szakaszra.",
    "budgets.investments.investment.already_added": "Ön már hozzáadta ezt a beruházási projektet.",
    "budgets.investments.investment.support_title": "A projekt támogatása",
    "budgets.investments.investment.supports.other": "%{count} támogatás",
    "budgets.investments.header.check_ballot": "Szavazataim ellenőrzése",
    "budgets.investments.header.different_heading_assigned": "Másik kategóriában is vannak aktív szavazatai: %{heading_link}.",
    "budgets.investments.header.change_ballot": "Ha meggondolja magát, a %{check_ballot} oldalon eltávolíthatja szavazatait, majd újrakezdheti.",
    "budgets.investments.header.check_ballot_link": "ellenőrizze szavazatait",
    "budgets.investments.header.price": "Teljes költségkeret",
    "budgets.investments.votes.confirm_group.one": "Beruházási projekteket csak a(z) %{count}. kerületben támogathat. Ha folytatja, később nem módosíthatja ezt a választást. Biztos benne?",
    "budgets.investments.votes.confirm_group.other": "Beruházási projekteket csak a következő kerületekben támogathatja: %{count}. Ha folytatja, később nem módosíthatja ezt a választást. Biztos benne?",
    "budgets.investments.votes.remove_support_label": "%{investment} támogatásának eltávolítása",
    "budgets.investments_list.investment.read_more": "További részletek",
    "budgets.investments_list.investment.supports": "Támogatások",
    "budgets.investments_list.see_all": "Az összes beruházási projekt megtekintése",
    "budgets.investments_list.title": "Beruházási projektek listája",
    "budgets.supports_info.next": "Támogassa azokat a projekteket, amelyeket szeretne a következő szakaszba juttatni.",
    "budgets.supports_info.scrolling": "Görgessen tovább az összes ötlet megtekintéséhez.",
    "budgets.supports_info.share": "Ossza meg a támogatott projekteket a közösségi médiában, hogy több figyelmet és támogatást kapjanak!",
    "budgets.supports_info.supported.one": "Eddig <strong>1 projektet</strong> támogatott.",
    "budgets.supports_info.supported.other": "Eddig <strong>%{count} projektet</strong> támogatott.",
    "budgets.supports_info.supported_not_logged_in": "Jelentkezzen be, hogy <strong>támogathassa a projekteket</strong>.",
    "budgets.supports_info.time": "%{phase_end_date}-ig még támogathat projekteket.",
    "budgets.supports_info.title": "Itt az idő, hogy <strong>támogassa</strong> a projekteket!",
    "budgets.results.heading": "A közösségi költségvetés eredményei",
    "budgets.results.heading_selection_title": "Kerület szerint",
    "budgets.results.ballot_lines_count": "Szavazatok",
    "budgets.results.hide_discarded_link": "Elvetettek elrejtése",
    "budgets.results.show_all_link": "Összes megjelenítése",
    "budgets.results.accepted": "Elfogadott beruházási projekt:",
    "budgets.results.discarded": "Elvetett beruházási projekt:",
    "budgets.results.incompatibles": "Összeférhetetlenek",
    "budgets.results.investment_title": "Projekt címe",
    "budgets.results.unfeasible_investment_proyects": "Nem megvalósítható beruházási projektek listája",
    "budgets.results.not_selected_investment_proyects": "A szavazásra ki nem választott beruházási projektek listája",
    "budgets.executions.page_title": "%{budget} – mérföldkövek",
    "budgets.executions.heading": "A közösségi költségvetés mérföldkövei",
    "budgets.executions.heading_selection_title": "Kerület szerint",
    "budgets.executions.no_winner_investments": "Ebben az állapotban nincs nyertes beruházási projekt.",
    "budgets.executions.filters.status.all": "Mind (%{count})",
    "budgets.executions.filters.milestone_tag.label": "Mérföldkőcímke",
    "budgets.executions.filters.milestone_tag.all": "Mind (%{count})",
    "budgets.phases.errors.dates_range_invalid": "A kezdő dátum nem lehet azonos a záró dátummal, és nem lehet annál későbbi sem.",
    "budgets.phases.errors.prev_phase_dates_invalid": "A kezdő dátumnak későbbinek kell lennie, mint az előző engedélyezett szakasz kezdő dátuma (%{phase_name}).",
    "budgets.phases.errors.next_phase_dates_invalid": "A záró dátumnak korábbinak kell lennie, mint a következő engedélyezett szakasz záró dátuma (%{phase_name}).",
}


def read(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    output: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            output.update(flatten(child, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            output.update(flatten(child, f"{prefix}[{index}]"))
    else:
        output[prefix] = value
    return output


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
    english = flatten(read(EN_PATH).get("en", {}))
    document = read(HU_PATH)
    hungarian = document.setdefault("hu", {})
    current = flatten(hungarian)
    changes = []
    for key, revised in OVERRIDES.items():
        if key not in english:
            raise KeyError(f"Unknown English locale key: {key}")
        previous = current.get(key, "")
        if previous != revised:
            set_path(hungarian, key, revised)
            changes.append(("budgets.yml", key, previous, revised, english[key], "human editorial revision"))
    HU_PATH.write_text(yaml.safe_dump(document, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    header = not CHANGELOG.exists()
    with CHANGELOG.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        if header:
            writer.writerow(["file", "key", "previous_hungarian", "revised_hungarian", "english_source", "method"])
        writer.writerows(changes)
    print(f"Applied {len(changes)} human editorial overrides to budgets.yml")


if __name__ == "__main__":
    main()
