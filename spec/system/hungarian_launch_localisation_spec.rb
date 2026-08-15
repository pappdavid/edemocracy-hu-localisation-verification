require "rails_helper"

describe "Hungarian launch localisation" do
  scenario "uses formal Hungarian on the login and registration screens" do
    visit new_user_session_path(locale: :hu)

    expect(page).to have_content "Bejelentkezés"
    expect(page).to have_content "Emlékezzen rám"
    expect(page).to have_button "Belépés"
    expect(page).not_to have_content "Sign in"

    visit new_user_registration_path(locale: :hu)

    expect(page).to have_content "Regisztráció"
    expect(page).to have_content "Jelszó megerősítése"
    expect(page).to have_content "A regisztrációval elfogadja"
    expect(page).not_to have_content "Register"
  end

  scenario "uses Hungarian header and footer wording" do
    visit root_path(locale: :hu)

    expect(page).to have_content "Viták"
    expect(page).to have_content "Javaslatok"
    expect(page).to have_content "Közösségi jogalkotás"
    expect(page).to have_content "Nyelv:"
    expect(page).to have_content "Szóljon bele abba, hogyan alakuljon a város"
    expect(page).not_to have_content "angol"
    expect(page).not_to have_content "Nyílt korányzat"
  end

  scenario "uses consistent debate and proposal terminology on public index pages" do
    visit debates_path(locale: :hu)

    expect(page).to have_content "Viták"
    expect(page).to have_content "Segítség a vitákhoz"
    expect(page).to have_content "Vita indítása"
    expect(page).not_to have_content "Debates"

    visit proposals_path(locale: :hu)

    expect(page).to have_content "Javaslatok"
    expect(page).to have_content "Segítség a javaslatokhoz"
    expect(page).to have_content "Javaslat létrehozása"
    expect(page).not_to have_content "Help with proposals"
  end

  scenario "keeps help wording technically neutral and free of the recorded outcome promise" do
    visit help_path(locale: :hu)

    expect(page).to have_content "Viták"
    expect(page).to have_content "Javaslatok"
    expect(page).to have_content "polgári javaslatok"
    expect(page).not_to have_content "elfogadja és végrehajtja"
  end
end
