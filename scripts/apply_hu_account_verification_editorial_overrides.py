#!/usr/bin/env python3
"""Apply human-edited Hungarian wording to authentication and verification journeys."""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "docs/hungarian_localisation_editorial_manual_changes.tsv"

OVERRIDES: dict[str, dict[str, str]] = {
    "devise_views.yml": {
        "devise_views.confirmations.new.submit": "Megerősítési utasítások újbóli elküldése",
        "devise_views.confirmations.new.title": "Megerősítési utasítások újbóli elküldése",
        "devise_views.confirmations.show.instructions": "Erősítse meg fiókját a(z) %{email} e-mail-címen keresztül.",
        "devise_views.confirmations.show.new_password_confirmation_label": "Új jelszó megerősítése",
        "devise_views.confirmations.show.new_password_label": "Új jelszó",
        "devise_views.confirmations.show.please_set_password": "Kérjük, adja meg új jelszavát. Ezzel a fenti e-mail-címmel is bejelentkezhet majd.",
        "devise_views.confirmations.show.submit": "Fiók megerősítése",
        "devise_views.confirmations.show.title": "Fiók megerősítése",
        "devise_views.mailer.confirmation_instructions.confirm_link": "Fiókom megerősítése",
        "devise_views.mailer.confirmation_instructions.text": "Az alábbi hivatkozásra kattintva erősítheti meg e-mail-címét:",
        "devise_views.mailer.reset_password_instructions.change_link": "Jelszavam módosítása",
        "devise_views.mailer.reset_password_instructions.hello": "Üdvözöljük",
        "devise_views.mailer.reset_password_instructions.ignore_text": "Ha nem Ön kezdeményezte a jelszó módosítását, hagyja figyelmen kívül ezt az e-mailt.",
        "devise_views.mailer.reset_password_instructions.info_text": "Jelszava csak akkor változik meg, ha megnyitja a hivatkozást és új jelszót ad meg.",
        "devise_views.mailer.reset_password_instructions.text": "Jelszó-visszaállítási kérelmet kaptunk. Az alábbi hivatkozásra kattintva adhat meg új jelszót:",
        "devise_views.mailer.reset_password_instructions.title": "Jelszó módosítása",
        "devise_views.mailer.unlock_instructions.hello": "Üdvözöljük",
        "devise_views.mailer.unlock_instructions.info_text": "Fiókját túl sok sikertelen bejelentkezési kísérlet miatt zároltuk.",
        "devise_views.mailer.unlock_instructions.instructions_text": "Fiókja feloldásához kattintson az alábbi hivatkozásra:",
        "devise_views.mailer.unlock_instructions.title": "Fiókja zárolva van",
        "devise_views.mailer.unlock_instructions.unlock_link": "Fiókom feloldása",
        "devise_views.menu.login_items.login": "Bejelentkezés",
        "devise_views.menu.login_items.logout": "Kijelentkezés",
        "devise_views.menu.login_items.signup": "Regisztráció",
        "devise_views.organizations.registrations.new.password_confirmation_label": "Jelszó megerősítése",
        "devise_views.organizations.registrations.new.responsible_name_note": "Adja meg annak a személynek a nevét, aki a szervezetet vagy közösséget képviseli, és a nevében javaslatokat nyújt be.",
        "devise_views.organizations.registrations.new.submit": "Regisztráció",
        "devise_views.organizations.registrations.new.title": "Regisztráció szervezetként vagy közösségként",
        "devise_views.organizations.registrations.success.back_to_index": "Értem, vissza a főoldalra",
        "devise_views.organizations.registrations.success.instructions_1": "<strong>Hamarosan felvesszük Önnel a kapcsolatot</strong>, hogy ellenőrizzük képviseleti jogosultságát.",
        "devise_views.organizations.registrations.success.instructions_2": "Amíg <strong>a szervezet ellenőrzése folyamatban van</strong>, küldtünk egy <strong>fiókmegerősítő hivatkozást</strong>.",
        "devise_views.organizations.registrations.success.instructions_3": "A megerősítés után nem ellenőrzött szervezetként is részt vehet a folyamatokban.",
        "devise_views.organizations.registrations.success.thank_you": "Köszönjük, hogy regisztrálta szervezetét vagy közösségét. A regisztráció jelenleg <strong>ellenőrzés alatt áll</strong>.",
        "devise_views.organizations.registrations.success.title": "Szervezet vagy közösség regisztrációja",
        "devise_views.passwords.edit.change_submit": "Jelszó módosítása",
        "devise_views.passwords.edit.password_confirmation_label": "Új jelszó megerősítése",
        "devise_views.passwords.edit.password_label": "Új jelszó",
        "devise_views.passwords.edit.title": "Jelszó módosítása",
        "devise_views.passwords.new.send_submit": "Utasítások elküldése",
        "devise_views.passwords.new.title": "Elfelejtette a jelszavát?",
        "devise_views.sessions.new.remember_me": "Emlékezzen rám",
        "devise_views.sessions.new.submit": "Bejelentkezés",
        "devise_views.sessions.new.title": "Bejelentkezés",
        "devise_views.shared.links.login": "Bejelentkezés",
        "devise_views.shared.links.new_confirmation": "Nem kapta meg a fiók aktiválásához szükséges utasításokat?",
        "devise_views.shared.links.new_password": "Elfelejtette a jelszavát?",
        "devise_views.shared.links.new_unlock": "Nem kapta meg a fiók feloldásához szükséges utasításokat?",
        "devise_views.shared.links.signup": "Nincs még fiókja? %{signup_link}",
        "devise_views.shared.links.signup_link": "Regisztráljon",
        "devise_views.unlocks.new.email_label": "E-mail-cím",
        "devise_views.unlocks.new.submit": "Feloldási utasítások újbóli elküldése",
        "devise_views.unlocks.new.title": "Feloldási utasítások újbóli elküldése",
        "devise_views.users.registrations.delete_form.erase_reason_label": "Indok",
        "devise_views.users.registrations.delete_form.info": "Ez a művelet nem vonható vissza. Kérjük, csak akkor folytassa, ha biztos a döntésében.",
        "devise_views.users.registrations.delete_form.info_reason": "Ha szeretné, megadhatja a törlés okát is; ez nem kötelező.",
        "devise_views.users.registrations.delete_form.submit": "Fiókom törlése",
        "devise_views.users.registrations.delete_form.title": "Fiók törlése",
        "devise_views.users.registrations.edit.email_label": "E-mail-cím",
        "devise_views.users.registrations.edit.leave_blank": "Hagyja üresen, ha nem kívánja módosítani.",
        "devise_views.users.registrations.edit.need_current": "A módosítások mentéséhez adja meg jelenlegi jelszavát.",
        "devise_views.users.registrations.edit.password_confirmation_label": "Új jelszó megerősítése",
        "devise_views.users.registrations.edit.update_submit": "Módosítások mentése",
        "devise_views.users.registrations.edit.waiting_for": "Megerősítésre vár:",
        "devise_views.users.registrations.new.cancel": "Regisztráció megszakítása",
        "devise_views.users.registrations.new.organization_signup": "Szervezetet vagy közösséget képvisel? %{signup_link}",
        "devise_views.users.registrations.new.organization_signup_link": "Regisztráljon itt",
        "devise_views.users.registrations.new.password_confirmation_label": "Jelszó megerősítése",
        "devise_views.users.registrations.new.submit": "Regisztráció",
        "devise_views.users.registrations.new.terms": "A regisztrációval elfogadja a(z) %{terms}.",
        "devise_views.users.registrations.new.terms_link": "felhasználási feltételeket",
        "devise_views.users.registrations.new.title": "Regisztráció",
        "devise_views.users.registrations.new.username_is_available": "A felhasználónév elérhető.",
        "devise_views.users.registrations.new.username_is_not_available": "Ez a felhasználónév már foglalt.",
        "devise_views.users.registrations.new.username_note": "Ez a név jelenik meg a hozzászólásai mellett.",
        "devise_views.users.registrations.success.back_to_index": "Értem, vissza a főoldalra",
        "devise_views.users.registrations.success.instructions_1": "Kérjük, ellenőrizze e-mailjeit: küldtünk egy <b>fiókmegerősítő hivatkozást</b>.",
        "devise_views.users.registrations.success.instructions_2": "Az e-mail-cím megerősítése után megkezdheti a részvételt.",
        "devise_views.users.registrations.success.verification_title": "Következő lépés: személyazonosság ellenőrzése",
        "devise_views.users.registrations.success.verification_instructions": "E-mail-címe megerősítése és bejelentkezés után nyissa meg a Saját fiók oldalt, majd válassza a Fiókom ellenőrzése lehetőséget. Itt elvégezheti az ellenőrzött részvételhez szükséges lakóhely- és személyazonosság-ellenőrzést.",
        "devise_views.users.registrations.success.thank_you": "Köszönjük a regisztrációját. A folytatáshoz <b>erősítse meg e-mail-címét</b>.",
        "devise_views.users.registrations.success.title": "E-mail-cím megerősítése",
    },
    "verification.yml": {
        "verification.alert.lock": "Elérte a megengedett próbálkozások számát. Kérjük, próbálja meg később.",
        "verification.back": "Vissza a Saját fiókhoz",
        "verification.email.create.alert.failure": "Nem sikerült megerősítő e-mailt küldeni a fiókjához.",
        "verification.email.create.flash.success": "Megerősítő e-mailt küldtünk a következő címre: %{email}.",
        "verification.email.show.alert.failure": "A megerősítő kód hibás.",
        "verification.email.show.flash.success": "Fiókja ellenőrzött státuszú.",
        "verification.letter.alert.unconfirmed_code": "Még nem adta meg a megerősítő kódot.",
        "verification.letter.create.flash.success": "Köszönjük, hogy igényelte <b>maximális biztonsági kódját (ez csak a végső szavazásokhoz szükséges)</b>. Néhány napon belül elküldjük a nyilvántartásunkban szereplő címre. Ha szeretné, személyesen is átveheti a kódot bármelyik ügyfélszolgálati irodában.",
        "verification.letter.edit.title": "Levél igényelve",
        "verification.letter.errors.incorrect_code": "A megerősítő kód hibás.",
        "verification.letter.new.explanation": "A költségvetési projektekre történő szavazáshoz a következő lehetőségek állnak rendelkezésre:",
        "verification.letter.new.office": "Személyes ellenőrzés ügyfélszolgálati irodában",
        "verification.letter.new.send_letter": "Kérem a kódot tartalmazó levelet",
        "verification.letter.new.title": "Gratulálunk!",
        "verification.letter.new.user_permission_info": "Fiókjával a következőket teheti:",
        "verification.letter.update.flash.success": "A kód helyes. Fiókja ellenőrzése sikeres.",
        "verification.redirect_notices.already_verified": "Fiókja már ellenőrzött.",
        "verification.redirect_notices.email_already_sent": "Már küldtünk egy megerősítő hivatkozást e-mailben. Ha nem találja az üzenetet, itt újra kérheti.",
        "verification.residence.alert.unconfirmed_residency": "A lakóhely ellenőrzése még nem történt meg.",
        "verification.residence.create.flash.success": "Lakóhelyének ellenőrzése sikeresen megtörtént.",
        "verification.residence.new.accept_terms_text": "Elfogadom a névjegyzékhez való hozzáférés %{terms_url}.",
        "verification.residence.new.document_number": "Okmányazonosító",
        "verification.residence.new.document_number_help_title": "Okmányszám formátuma",
        "verification.residence.new.error_not_allowed_age": "Nem érte el a részvételhez szükséges alsó korhatárt.",
        "verification.residence.new.error_not_allowed_postal_code": "Az irányítószáma alapján nem jogosult a részvételre.",
        "verification.residence.new.error_verifying_census": "A nyilvántartás alapján nem sikerült ellenőrizni az adatait. Kérjük, ellenőrizze az adatokat, majd szükség esetén forduljon az önkormányzathoz vagy az ügyfélszolgálathoz.",
        "verification.residence.new.form_errors": "hiba miatt nem sikerült ellenőrizni a lakóhelyét",
        "verification.residence.new.postal_code_note": "A fiók ellenőrzéséhez adja meg lakóhelyének irányítószámát.",
        "verification.residence.new.terms": "hozzáférési feltételeit",
        "verification.residence.new.title": "Lakóhely ellenőrzése",
        "verification.residence.new.verify_residence": "Lakóhely ellenőrzése",
        "verification.sms.create.flash.success": "Adja meg az SMS-ben kapott megerősítő kódot.",
        "verification.sms.edit.resend_sms_link": "SMS újbóli elküldése",
        "verification.sms.edit.resend_sms_text": "Nem érkezett meg a megerősítő kódot tartalmazó SMS?",
        "verification.sms.edit.submit_button": "Kód ellenőrzése",
        "verification.sms.edit.title": "Megerősítő kód megadása",
        "verification.sms.new.phone": "Adja meg mobiltelefonszámát a kód fogadásához.",
        "verification.sms.new.phone_note": "Telefonszámát kizárólag a kód elküldésére használjuk; kapcsolatfelvétel céljára nem.",
        "verification.sms.new.submit_button": "Kód küldése",
        "verification.sms.new.title": "Megerősítő kód küldése",
        "verification.sms.update.error": "A megerősítő kód hibás.",
        "verification.sms.update.flash.level_three.success": "A kód helyes. Fiókja ellenőrzött státuszú.",
        "verification.sms.update.flash.level_two.success": "A kód helyes.",
        "verification.step_1": "Lakóhely",
        "verification.step_2": "Megerősítő kód",
        "verification.step_3": "Végső ellenőrzés",
        "verification.user_permission_debates": "Részvétel a vitákban",
        "verification.user_permission_info": "Az adatok ellenőrzésével a következőket teheti:",
        "verification.user_permission_proposal": "Új javaslatok létrehozása",
        "verification.user_permission_support_proposal": "Javaslatok támogatása",
        "verification.user_permission_votes": "Szavazás a közösségi költségvetés projektjeiről",
        "verification.verification_needed": "További ellenőrzés szükséges",
        "verification.verified_user.form.submit_button": "Kód küldése",
        "verification.verified_user.show.email_title": "E-mail-címek",
        "verification.verified_user.show.explanation": "A nyilvántartásban az alábbi adatok szerepelnek. Kérjük, válassza ki, hogyan szeretné megkapni a megerősítő kódot.",
        "verification.verified_user.show.phone_title": "Telefonszámok",
        "verification.verified_user.show.title": "Rendelkezésre álló adatok",
        "verification.verified_user.show.use_another_phone": "Másik telefonszám használata",
    },
}


def load(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            result.update(flatten(child, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            result.update(flatten(child, f"{prefix}[{index}]"))
    else:
        result[prefix] = value
    return result


def set_path(target: dict[str, Any], path: str, value: Any) -> None:
    current: Any = target
    parts: list[str | int] = []
    for match in re.finditer(r"([^\.\[\]]+)|\[(\d+)\]", path):
        parts.append(int(match.group(2)) if match.group(2) is not None else match.group(1))
    for index, part in enumerate(parts):
        final = index == len(parts) - 1
        if final:
            current[part] = value
        else:
            next_is_list = isinstance(parts[index + 1], int)
            if part not in current:
                current[part] = [] if next_is_list else {}
            current = current[part]


def main() -> None:
    all_changes = []
    for filename, overrides in OVERRIDES.items():
        en_path = ROOT / "config/locales/en" / filename
        hu_path = ROOT / "config/locales/hu-HU" / filename
        english = flatten(load(en_path).get("en", {}))
        document = load(hu_path)
        hungarian = document.setdefault("hu", {})
        current = flatten(hungarian)
        for key, revised in overrides.items():
            if key not in english:
                raise KeyError(f"Unknown English locale key in {filename}: {key}")
            previous = current.get(key, "")
            if previous != revised:
                set_path(hungarian, key, revised)
                all_changes.append((filename, key, previous, revised, english[key], "human editorial revision"))
        hu_path.write_text(yaml.safe_dump(document, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    header = not CHANGELOG.exists()
    with CHANGELOG.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        if header:
            writer.writerow(["file", "key", "previous_hungarian", "revised_hungarian", "english_source", "method"])
        writer.writerows(all_changes)
    print(f"Applied {len(all_changes)} human editorial overrides")


if __name__ == "__main__":
    main()
