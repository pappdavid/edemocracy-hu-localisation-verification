require "rails_helper"

describe "Registration verification flow" do
  scenario "explains the Hungarian verification next step after registration" do
    visit users_sign_up_success_path(locale: :hu)

    expect(page).to have_content "Következő lépés: személyazonosság ellenőrzése"
    expect(page).to have_content "E-mail-címe megerősítése és bejelentkezés után"
    expect(page).to have_content "Fiókom ellenőrzése"
  end

  scenario "takes a Hungarian signed-in user from My account into the verification wizard" do
    login_as(create(:user))

    visit account_path(locale: :hu)
    click_link "Fiókom ellenőrzése"

    expect(page).to have_current_path(new_residence_path, ignore_query: true)
    expect(page).to have_content "Lakóhely ellenőrzése"
    expect(page).to have_content "Személyi igazolvány"
  end
end
