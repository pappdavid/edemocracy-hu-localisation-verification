require "rails_helper"

describe "Hungarian residence verification" do
  before { create(:geozone) }

  scenario "shows reviewed Hungarian identity-verification copy and a working census-terms link" do
    login_as(create(:user))

    visit new_residence_path(locale: :hu)

    expect(page).to have_content "Lakóhely ellenőrzése"
    expect(page).to have_content "Lakóhely"
    expect(page).to have_content(/Megerősítő kód/i)
    expect(page).to have_content(/Végső ellenőrzés/i)
    expect(page).to have_select "residence_document_type",
                                with_options: ["Kérjük, válasszon", "Személyi igazolvány",
                                               "Útlevél", "Lakcímkártya"]
    expect(page).to have_content "Személyi igazolvány"
    expect(page).not_to have_content "DNI"
    expect(page).not_to have_content "__MASZK_"

    within_window(window_opened_by { click_link "hozzáférési feltételeit" }) do
      expect(page).to have_content "A névjegyzékhez való hozzáférés feltételei"
    end
  end
end
