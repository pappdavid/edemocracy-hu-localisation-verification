# Hungarian localisation editorial changelog

## Purpose and standard

This record documents the second-pass editorial revision of the Hungarian CONSUL 2.5.0 localisation. The first machine-generated wording was frequently literal and grammatically unnatural. The revision standard uses formal **Ön** address, clear civic-platform terminology, natural Hungarian word order, and consistent labels for accounts, registration, proposals, votes, participatory budgeting, verification, and residence checking.

Rails variables, HTML, URLs, Markdown destinations, protocol names, browser names, brands, and formatting tokens are retained verbatim where they are application syntax or identifiers rather than Hungarian prose.

## Revision totals

| Change class | Changed locale leaves | Description |
|---|---:|---|
| Full-catalogue neural editorial draft | 3,135 | All canonical English locale files were revisited through a checkpointed, token-preserving Hungarian draft pass. |
| Human editorial corrections | 411 | High-visibility registration, verification, participatory-budget, navigation, debate, proposal, poll, search, and shared-interface strings were rewritten manually. |

## Automated-draft changes by locale file

| Locale file | Changed leaves |
|---|---:|
| `activemodel.yml` | 12 |
| `activerecord.yml` | 228 |
| `admin.yml` | 892 |
| `budgets.yml` | 132 |
| `community.yml` | 20 |
| `devise.yml` | 43 |
| `devise_views.yml` | 76 |
| `documents.yml` | 10 |
| `general.yml` | 501 |
| `images.yml` | 15 |
| `kaminari.yml` | 6 |
| `legislation.yml` | 59 |
| `mailers.yml` | 93 |
| `management.yml` | 77 |
| `milestones.yml` | 4 |
| `moderation.yml` | 52 |
| `officing.yml` | 43 |
| `pages.yml` | 32 |
| `rails.yml` | 91 |
| `rails_date_order.yml` | 3 |
| `responders.yml` | 30 |
| `sdg.yml` | 381 |
| `sdg_management.yml` | 17 |
| `seeds.yml` | 46 |
| `settings.yml` | 187 |
| `social_share_button.yml` | 6 |
| `stats.yml` | 22 |
| `valuation.yml` | 39 |
| `verification.yml` | 18 |

## Human editorial corrections by locale file

| Locale file | Changed leaves | Focus |
|---|---:|---|
| `activemodel.yml` | 2 | Editorial correction |
| `activerecord.yml` | 10 | Editorial correction |
| `admin.yml` | 15 | Editorial correction |
| `budgets.yml` | 108 | Community-budget votes, project creation, ballots, results, and phases |
| `devise_views.yml` | 74 | Registration, login, password recovery, account confirmation, and organisation registration |
| `general.yml` | 150 | Navigation, comments, debates, proposals, polls, dashboard, search, shared actions, and notifications |
| `management.yml` | 1 | Editorial correction |
| `rails.yml` | 3 | Editorial correction |
| `sdg.yml` | 2 | Editorial correction |
| `seeds.yml` | 1 | Editorial correction |
| `settings.yml` | 3 | Editorial correction |
| `social_share_button.yml` | 1 | Editorial correction |
| `stats.yml` | 2 | Editorial correction |
| `valuation.yml` | 1 | Editorial correction |
| `verification.yml` | 38 | Residence checks, consent, SMS, confirmation codes, and verified-account wording |

## Representative human-edited changes

| Locale key | Previous wording | Revised wording | Editorial rationale |
|---|---|---|---|
| `budgets.ballots.show.title` | A szavazólapod | Az Ön szavazólapja | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.show.amount_available.knapsack` | Továbbra is elérhető az Ön számára: <span>%{count}</span> | Még felhasználható: <span>%{count}</span> | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.show.amount_available.approval.zero` | Még mindig <span>%{count}</span> szavazatot adhat le. | Még <span>%{count}</span> szavazatot adhat le. | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.show.amount_available.approval.one` | Még mindig <span>%{count}</span> szavazatot adhat le. | Még <span>%{count}</span> szavazatot adhat le. | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.show.amount_available.approval.other` | Még mindig <span>%{count}</span> szavazatot adhat le. | Még <span>%{count}</span> szavazatot adhat le. | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.show.amount_limit.approval.one` | Szavazhat <span>1</span> projektre | Legfeljebb <span>1</span> projektre szavazhat. | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.show.amount_limit.approval.other` | Legfeljebb <span>%{count}</span> projektre szavazhat | Legfeljebb <span>%{count}</span> projektre szavazhat. | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.show.no_balloted_group_yet` | Még nem szavazott erre a csoportra, menjen szavazni! | Ebben a kategóriában még nem szavazott. Adja le szavazatát most! | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.show.remove_label` | Távolítsa el szavazatát %{investment} | Szavazat eltávolítása: %{investment} | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.show.voted.one` | Ön <span>egy</span> befektetésre szavazott. | Ön <span>egy</span> beruházási projektre szavazott. | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.show.voted.other` | Ön <span>%{count}</span> befektetésre szavazott. | Ön <span>%{count}</span> beruházási projektre szavazott. | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.show.voted_info` | Szavazásod megerősítésre került! | Szavazata megerősítést nyert. | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.show.voted_info_2` | De bármikor megváltoztathatja szavazatát, amíg ez a szakasz le nem zárul. | Szavazatát a szakasz lezárásáig bármikor módosíthatja. | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.reasons_for_not_balloting.not_verified` | Csak ellenőrzött felhasználók szavazhatnak a befektetésekre; %{verify_account}. | Beruházási projektekre csak ellenőrzött felhasználók szavazhatnak; %{verify_account}. | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.reasons_for_not_balloting.not_selected` | A ki nem választott beruházási projektek nem támogathatók | A végső szavazásra ki nem választott beruházási projektek nem támogathatók. | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.reasons_for_not_balloting.not_enough_money` | Már hozzárendelte a rendelkezésre álló költségkeretet.<br><small>Ne feledje, hogy bármikor %{change_ballot}-t tehet</small> | Már felhasználta a rendelkezésre álló költségkeretet.<br><small>Ne feledje: bármikor %{change_ballot}.</small> | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.reasons_for_not_balloting.no_ballots_allowed` | A kiválasztási fázis lezárult | A kiválasztási szakasz lezárult. | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.reasons_for_not_balloting.different_heading_assigned` | Már szavazott egy másik címsorra: %{heading_link} | Már egy másik kategóriában szavazott: %{heading_link}. | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.reasons_for_not_balloting.not_enough_available_votes` | Elérte a szavazatok maximális számát | Elérte a leadható szavazatok maximális számát. | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.reasons_for_not_balloting.change_ballot` | változtassa meg a szavazatait | módosíthatja szavazatait | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.ballots.reasons_for_not_balloting.casted_offline` | Már offline is részt vett | Ön már személyesen is részt vett a szavazásban. | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.groups.show.title` | Válasszon egy címsort | Válasszon kategóriát | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.phase.drafting` | Piszkozat (Nyilvánosan nem látható) | Piszkozat (nyilvánosan nem látható) | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.phase.informing` | Információ | Tájékoztatás | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.phase.publishing_prices` | Kiadói projektek árai | A projektek költségének közzététele | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.phase.balloting` | Szavazási projektek | Szavazás a projektekről | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.phase.reviewing_ballots` | Szavazás felülvizsgálata | A szavazás ellenőrzése | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.phase.finished` | Kész költségvetés | Lezárt költségvetés | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.index.title` | közösségi költségvetések | Közösségi költségvetések | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.index.section_header.icon_alt` | közösségi költségvetések ikonra | Közösségi költségvetés ikon | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.index.section_header.title` | közösségi költségvetések | Közösségi költségvetések | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.index.next_phase` | Következő fázis | Következő szakasz | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.index.prev_phase` | Előző fázis | Előző szakasz | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.index.current_phase` | Aktuális fázis | Aktuális szakasz | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.index.map` | A költségvetési beruházási javaslatok földrajzi elhelyezkedésűek | Beruházási javaslatok a térképen | Formal Hungarian grammar, natural civic terminology, or clearer user action. |
| `budgets.index.finished_budgets` | Elkészült a közösségi költségvetés | Lezárt közösségi költségvetések | Formal Hungarian grammar, natural civic terminology, or clearer user action. |

## Complete machine-readable audit trails

The complete per-key before/after records are retained in the following tab-separated files, including the English source value for every changed leaf:

- `docs/hungarian_localisation_editorial_changes.tsv` — full-catalogue checkpointed editorial draft changes.
- `docs/hungarian_localisation_editorial_manual_changes.tsv` — reviewed human corrections for the highest-visibility user journeys.

## Validation requirements

Before release, run the locale coverage audit and both source validators. Validate the Hungarian registration and identity-verification journey in the isolated synthetic preview. A final native-speaker review remains advisable for long-form policy, SDG, and administrative explanatory text before public production release.
